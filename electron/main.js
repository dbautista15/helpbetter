const { app, BrowserWindow, ipcMain } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const readline = require("readline");

let mainWindow;
let pythonProcess;
let pythonReady = false;

// Start Python subprocess
function startPythonProcess() {
  const pythonScript = path.join(
    __dirname,
    "..",
    "backend",
    "electron_bridge.py"
  );
  const pythonExe = "python"; // For now, use system Python

  console.log("🐍 Starting Python subprocess...");
  console.log(`Script path: ${pythonScript}`);

  pythonProcess = spawn(pythonExe, [pythonScript], {
    cwd: path.join(__dirname, ".."),
    env: {
      ...process.env,
      PYTHONUNBUFFERED: "1",
      DB_PATH: path.join(app.getPath("userData"), "journal.db"),
    },
  });

  // Read Python output line by line
  const rl = readline.createInterface({
    input: pythonProcess.stdout,
    crlfDelay: Infinity,
  });

  rl.on("line", (line) => {
    try {
      const message = JSON.parse(line);
      console.log("📨 Received from Python:", message.type);

      if (message.type === "ready") {
        pythonReady = true;
        console.log("✅ Python is ready!");
      } else if (message.type === "response") {
        mainWindow.webContents.send("python-response", message.data);
      } else if (message.type === "error") {
        console.error("❌ Python error:", message.error);
        mainWindow.webContents.send("python-error", message.error);
      }
    } catch (e) {
      // Not JSON, just a log message
      console.log(`[Python] ${line}`);
    }
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`[Python Error] ${data}`);
  });

  pythonProcess.on("close", (code) => {
    console.log(`Python process exited with code ${code}`);
    pythonReady = false;
  });
}

// Send command to Python
function sendToPython(command, data) {
  if (!pythonReady) {
    throw new Error("Python subprocess not ready");
  }

  const message = JSON.stringify({ command, data }) + "\n";
  pythonProcess.stdin.write(message);
  console.log(`📤 Sent to Python: ${command}`);
}

// Create the app window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, "preload.js"),
    },
    autoHideMenuBar: true,
    backgroundColor: "#ffffff",
  });

  // For now, just show a simple HTML page
  // Later we'll load your React app
  mainWindow.loadFile(path.join(__dirname, "index.html"));
  mainWindow.webContents.openDevTools(); // Open DevTools automatically
}

// IPC Handler: Create Entry
ipcMain.handle("create-entry", async (event, entryData) => {
  console.log("📝 Creating entry:", entryData);

  return new Promise((resolve, reject) => {
    const responseHandler = (event, response) => {
      mainWindow.webContents.removeListener("python-response", responseHandler);
      resolve(response);
    };

    const errorHandler = (event, error) => {
      mainWindow.webContents.removeListener("python-error", errorHandler);
      reject(new Error(error));
    };

    mainWindow.webContents.once("python-response", responseHandler);
    mainWindow.webContents.once("python-error", errorHandler);

    sendToPython("create_entry", entryData);

    setTimeout(() => {
      mainWindow.webContents.removeListener("python-response", responseHandler);
      mainWindow.webContents.removeListener("python-error", errorHandler);
      reject(new Error("Python subprocess timeout"));
    }, 30000);
  });
});

// IPC Handler: Get Entries
ipcMain.handle("get-entries", async (event, limit = 20) => {
  return new Promise((resolve, reject) => {
    const responseHandler = (event, response) => {
      mainWindow.webContents.removeListener("python-response", responseHandler);
      resolve(response);
    };

    mainWindow.webContents.once("python-response", responseHandler);
    sendToPython("get_entries", { limit });

    setTimeout(() => {
      mainWindow.webContents.removeListener("python-response", responseHandler);
      reject(new Error("Timeout"));
    }, 5000);
  });
});

// App lifecycle
app.whenReady().then(() => {
  startPythonProcess();

  // Wait for Python before showing window
  const checkReady = setInterval(() => {
    if (pythonReady) {
      clearInterval(checkReady);
      createWindow();
    }
  }, 100);

  setTimeout(() => {
    if (!pythonReady) {
      clearInterval(checkReady);
      console.error("⚠️  Python failed to start");
      createWindow();
    }
  }, 10000);
});

app.on("window-all-closed", () => {
  if (pythonProcess) {
    pythonProcess.kill();
  }
  app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
