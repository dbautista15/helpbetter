const { contextBridge, ipcRenderer } = require("electron");

// Expose specific functions to the renderer process
contextBridge.exposeInMainWorld("electronAPI", {
  // Create journal entry
  createEntry: (data) => ipcRenderer.invoke("create-entry", data),

  // Get recent entries
  getEntries: (limit) => ipcRenderer.invoke("get-entries", limit),

  // Listen for Python errors
  onPythonError: (callback) => {
    ipcRenderer.on("python-error", (event, error) => callback(error));
  },
});

console.log("✅ Preload script loaded - electronAPI is available");
