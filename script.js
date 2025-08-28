// frontend/script.js
const API_BASE = "http://127.0.0.1:8000";
let lastNotifiedId = null; // prevents repeated notifications for same slot

async function fetchNow() {
  try {
    const res = await fetch(`${API_BASE}/now`);
    const data = await res.json();
    showNow(data.current);
    showNext(data.next);

    // notify when a new current session starts
    if (data.current) {
      const id = `${data.current.day || ''}|${data.current.subject}|${data.current.start}`;
      if (id !== lastNotifiedId) {
        notifyNow(data.current, data.next);
        lastNotifiedId = id;
      }
    }
  } catch (err) {
    console.error("Error fetching /now", err);
    document.getElementById("nowInfo").innerText = "Error contacting backend.";
    document.getElementById("nextInfo").innerText = "";
  }
}

async function fetchToday() {
  try {
    const res = await fetch(`${API_BASE}/today`);
    const data = await res.json();
    const container = document.getElementById("todayList");
    if (!data.sessions || data.sessions.length === 0) {
      container.innerText = `No sessions for ${data.day}`;
      return;
    }
    let html = `<strong>${data.day}</strong><ul>`;
    for (const s of data.sessions) {
      html += `<li>${s.start} - ${s.end} → ${s.subject}</li>`;
    }
    html += `</ul>`;
    container.innerHTML = html;
  } catch (err) {
    console.error("Error fetching /today", err);
    document.getElementById("todayList").innerText = "Error contacting backend.";
  }
}

function showNow(current) {
  const el = document.getElementById("nowInfo");
  if (!current) {
    el.innerHTML = `<div class="small">No class is running right now.</div>`;
    return;
  }
  el.innerHTML = `<div><strong>${current.subject}</strong></div>
                  <div class="small">${current.day || ''} • ${current.start} - ${current.end}</div>`;
}

function showNext(next) {
  const el = document.getElementById("nextInfo");
  if (!next) {
    el.innerHTML = `<div class="small">No upcoming session found.</div>`;
    return;
  }
  el.innerHTML = `<div><strong>${next.subject}</strong></div>
                  <div class="small">${next.day || ''} • ${next.start} - ${next.end}</div>`;
}

function notifyNow(current, next) {
  if (!current) return;
  const title = `Now: ${current.subject}`;
  let body = `${current.start} — ${current.end}`;
  if (next) body += `\nNext: ${next.subject} (${next.start} - ${next.end})`;
  if (Notification.permission === "granted") {
    new Notification(title, { body });
  } else {
    // nothing — user didn't allow notifications
    console.log("Notification blocked or not allowed");
  }
}

document.getElementById("btnRefresh").addEventListener("click", () => {
  fetchNow();
  fetchToday();
});
document.getElementById("btnPerm").addEventListener("click", async () => {
  const p = await Notification.requestPermission();
  alert("Notification permission: " + p);
});

// initial load
fetchNow();
fetchToday();
// poll every 20 seconds to detect session changes
setInterval(fetchNow, 20 * 1000);
