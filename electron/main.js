const { app, BrowserWindow, ipcMain } = require("electron");
const { spawn } = require("child_process");
const path = require("path");
const readline = require("readline");

let mainWindow;
let pythonProcess;
let pythonReady = false;

// Store pending requests with unique IDs
const pendingRequests = new Map();
let requestIdCounter = 0;

/**
 * Detect correct Python executable for the platform
 */
function getPythonExecutable() {
  if (app.isPackaged) {
    // Production: Use bundled Python
    const platform = process.platform;

    if (platform === "darwin") {
      // Mac: python-runtime/bin/python3
      return path.join(process.resourcesPath, "python", "bin", "python3");
    } else if (platform === "win32") {
      // Windows: python-runtime/Scripts/python.exe
      return path.join(
        process.resourcesPath,
        "python",
        "Scripts",
        "python.exe"
      );
    } else {
      // Linux: python-runtime/bin/python3
      return path.join(process.resourcesPath, "python", "bin", "python3");
    }
  } else {
    // Development: Use python-runtime venv
    const platform = process.platform;
    const runtimePath = path.join(__dirname, "python-runtime");

    if (platform === "darwin" || platform === "linux") {
      // Check if python-runtime exists
      const runtimePython = path.join(runtimePath, "bin", "python");
      if (require("fs").existsSync(runtimePython)) {
        console.log(`✅ Using python-runtime: ${runtimePython}`);
        return runtimePython;
      }
      return "python3";
    } else {
      // Windows
      const runtimePython = path.join(runtimePath, "Scripts", "python.exe");
      if (require("fs").existsSync(runtimePython)) {
        console.log(`✅ Using python-runtime: ${runtimePython}`);
        return runtimePython;
      }
      return "python";
    }
  }
}

/**
 * Start Python as a subprocess
 */
function startPythonProcess() {
  const pythonScript = path.join(
    __dirname,
    "..",
    "backend",
    "electron_bridge.py"
  );
  const pythonExe = getPythonExecutable();

  console.log("🐍 Starting Python subprocess...");
  console.log(`Python executable: ${pythonExe}`);
  console.log(`Script path: ${pythonScript}`);

  // Database path configuration
  // DEVELOPMENT: Use backend/journal.db (where demo data is)
  // PRODUCTION: Use proper OS location
  const dbPath = app.isPackaged
    ? path.join(app.getPath("userData"), "journal.db")
    : path.join(__dirname, "..", "backend", "journal.db");

  console.log(`Database path: ${dbPath}`);

  pythonProcess = spawn(pythonExe, [pythonScript], {
    cwd: path.join(__dirname, ".."),
    env: {
      ...process.env,
      PYTHONUNBUFFERED: "1",
      PYTHONIOENCODING: "utf-8",  // Fix emoji encoding on Windows
      DB_PATH: dbPath, // Tell Python which database to use
      RESOURCES_PATH: app.isPackaged 
        ? process.resourcesPath 
        : path.join(__dirname, ".."),  // Development: project root
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
        // Handle response with requestId
        const requestId = message.requestId;
        if (requestId !== undefined && pendingRequests.has(requestId)) {
          const { resolve } = pendingRequests.get(requestId);
          pendingRequests.delete(requestId);
          resolve(message.data);
        }
      } else if (message.type === "error") {
        console.error("❌ Python error:", message.error);
        const requestId = message.requestId;
        if (requestId !== undefined && pendingRequests.has(requestId)) {
          const { reject } = pendingRequests.get(requestId);
          pendingRequests.delete(requestId);
          reject(new Error(message.error));
        }
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

/**
 * Send command to Python with unique request ID
 */
function sendToPython(command, data) {
  if (!pythonReady) {
    throw new Error("Python subprocess not ready");
  }

  const requestId = requestIdCounter++;
  const message = JSON.stringify({ command, data, requestId }) + "\n";
  pythonProcess.stdin.write(message);
  console.log(`📤 Sent to Python: ${command} (ID: ${requestId})`);

  return requestId;
}

/**
 * Create the main window
 */
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

  // Load the test HTML page
  mainWindow.loadFile(path.join(__dirname, "dist", "index.html"));
  mainWindow.webContents.openDevTools();
}

/**
 * IPC HANDLERS - Fixed with request ID system
 */

// Create journal entry with ML analysis
ipcMain.handle("create-entry", async (event, entryData) => {
  console.log("📝 Creating entry:", entryData);

  return new Promise((resolve, reject) => {
    try {
      const requestId = sendToPython("create_entry", entryData);

      // Store the promise handlers
      pendingRequests.set(requestId, { resolve, reject });

      // Timeout after 30 seconds (ML can take time)
      setTimeout(() => {
        if (pendingRequests.has(requestId)) {
          pendingRequests.delete(requestId);
          reject(new Error("Python subprocess timeout"));
        }
      }, 30000);
    } catch (error) {
      reject(error);
    }
  });
});

// Get recent entries
ipcMain.handle("get-entries", async (event, limit = 20) => {
  return new Promise((resolve, reject) => {
    try {
      const requestId = sendToPython("get_entries", { limit });

      pendingRequests.set(requestId, { resolve, reject });

      setTimeout(() => {
        if (pendingRequests.has(requestId)) {
          pendingRequests.delete(requestId);
          reject(new Error("Timeout"));
        }
      }, 5000);
    } catch (error) {
      reject(error);
    }
  });
});

// Get statistics
ipcMain.handle("get-stats", async () => {
  return new Promise((resolve, reject) => {
    try {
      const requestId = sendToPython("get_stats", {});

      pendingRequests.set(requestId, { resolve, reject });

      setTimeout(() => {
        if (pendingRequests.has(requestId)) {
          pendingRequests.delete(requestId);
          reject(new Error("Timeout"));
        }
      }, 5000);
    } catch (error) {
      reject(error);
    }
  });
});

/**
 * App Lifecycle
 */
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
