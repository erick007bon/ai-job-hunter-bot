document.addEventListener('DOMContentLoaded', () => {
  const statusEl = document.getElementById('status');
  const timeEl = document.getElementById('time');
  const syncBtn = document.getElementById('syncBtn');

  // Cargar estado guardado
  function loadStatus() {
    chrome.storage.local.get(['lastSyncStatus', 'lastSyncTime'], (data) => {
      if (data.lastSyncStatus) {
        statusEl.textContent = data.lastSyncStatus;
        if (data.lastSyncStatus === 'Success') {
          statusEl.className = 'value success';
        } else {
          statusEl.className = 'value error';
        }
      }
      
      if (data.lastSyncTime) {
        timeEl.textContent = data.lastSyncTime;
      }
    });
  }

  loadStatus();

  // Forzar sincronizacion
  syncBtn.addEventListener('click', () => {
    syncBtn.textContent = 'Syncing...';
    syncBtn.disabled = true;
    
    chrome.runtime.sendMessage({ action: "forceSync" }, (response) => {
      setTimeout(() => {
        loadStatus();
        syncBtn.textContent = 'Force Sync Now';
        syncBtn.disabled = false;
      }, 1000);
    });
  });
});
