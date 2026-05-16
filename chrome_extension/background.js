// AI Job Hunter - Background Service Worker

const SYNC_SERVER_URL = "http://127.0.0.1:1337/sync";
let lastSyncTime = 0;

// Configurar alarma para revisar cookies cada hora
chrome.alarms.create("syncCookies", { periodInMinutes: 60 });

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "syncCookies") {
    syncLinkedInCookies();
  }
});

// También escuchar cuando se actualizan las cookies manualmente
chrome.cookies.onChanged.addListener((changeInfo) => {
  if (changeInfo.cookie.domain.includes("linkedin.com") && 
      (changeInfo.cookie.name === "li_at" || changeInfo.cookie.name === "JSESSIONID")) {
    
    // Evitar spam: solo sincronizar si pasaron al menos 5 minutos desde la última vez
    const now = Date.now();
    if (now - lastSyncTime > 5 * 60 * 1000) {
      console.log(`Cookie ${changeInfo.cookie.name} changed. Triggering sync.`);
      syncLinkedInCookies();
    }
  }
});

async function syncLinkedInCookies() {
  try {
    const liAtCookie = await chrome.cookies.get({ url: "https://www.linkedin.com", name: "li_at" });
    const jSessionIdCookie = await chrome.cookies.get({ url: "https://www.linkedin.com", name: "JSESSIONID" });

    if (!liAtCookie || !jSessionIdCookie) {
      console.log("No LinkedIn cookies found. User might not be logged in.");
      return;
    }

    const payload = {
      li_at: liAtCookie.value,
      jsessionid: jSessionIdCookie.value.replace(/['"]+/g, '') // Limpiar comillas si las tiene
    };

    const response = await fetch(SYNC_SERVER_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      lastSyncTime = Date.now();
      chrome.storage.local.set({ lastSyncStatus: "Success", lastSyncTime: new Date().toLocaleString() });
      console.log("Cookies synced successfully to local server!");
    } else {
      throw new Error(`Server returned ${response.status}`);
    }

  } catch (error) {
    console.error("Failed to sync cookies:", error);
    chrome.storage.local.set({ lastSyncStatus: `Error: ${error.message}`, lastSyncTime: new Date().toLocaleString() });
  }
}

// Forzar una sincronización al inicio
chrome.runtime.onStartup.addListener(() => {
  syncLinkedInCookies();
});

// Mensajes desde el popup para forzar sincronización manual
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "forceSync") {
    syncLinkedInCookies().then(() => sendResponse({ status: "done" }));
    return true; // Mantener puerto abierto para async response
  }
});
