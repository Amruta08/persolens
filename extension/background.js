const API_BASE = "http://127.0.0.1:8000";

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => { 
    if (msg.type !== "api") return;

    fetch(API_BASE + msg.path, { method: msg.method || "GET" })
    .then(async(res) => {
        let data = null;
        try{
            data = await res.json();
        } catch (e) {}
        sendResponse({ ok: res.ok, status: res.status, data });
    })
    .catch((err) => {
        sendResponse({ ok: false, status: 0, error: String(err) });
    });
    return true;
});