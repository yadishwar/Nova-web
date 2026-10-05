const STORAGE_KEY = "nova_chat_v1";
const chatEl = document.getElementById("chat");
const heroEl = document.getElementById("hero");
const inputEl = document.getElementById("input");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const scrollEl = document.querySelector(".container");

let messages = loadMessages();
let busy = false;

function loadMessages() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return Array.isArray(saved) ? saved : [];
  } catch (e) {
    return [];
  }
}

function saveMessages() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
  } catch (e) { /* storage unavailable; ignore */ }
}

function renderMarkdown(text) {
  if (window.marked && window.DOMPurify) {
    return DOMPurify.sanitize(marked.parse(text));
  }
  return null;
}

function addBubble(role, text, kind) {
  const row = document.createElement("div");
  row.className = "msg " + (kind || role);
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const html = role === "assistant" && !kind ? renderMarkdown(text) : null;
  if (html !== null) bubble.innerHTML = html;
  else bubble.textContent = text;
  row.appendChild(bubble);
  chatEl.appendChild(row);
  scrollToBottom();
  return row;
}

function addTyping() {
  const row = document.createElement("div");
  row.className = "msg assistant";
  row.innerHTML = '<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
  chatEl.appendChild(row);
  scrollToBottom();
  return row;
}

function scrollToBottom() {
  scrollEl.scrollTop = scrollEl.scrollHeight;
}

function updateHero() {
  heroEl.classList.toggle("hidden", messages.length > 0);
}

function setBusy(value) {
  busy = value;
  sendBtn.disabled = value;
  inputEl.disabled = value;
  if (!value) inputEl.focus();
}

function autoResize() {
  inputEl.style.height = "auto";
  inputEl.style.height = Math.min(inputEl.scrollHeight, 160) + "px";
}

async function sendMessage(text) {
  text = (text || "").trim();
  if (!text || busy) return;

  messages.push({ role: "user", content: text });
  saveMessages();
  addBubble("user", text);
  updateHero();
  inputEl.value = "";
  autoResize();
  setBusy(true);
  const typing = addTyping();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ messages: messages }),
    });
    let data = {};
    try { data = await res.json(); } catch (e) { /* non-JSON response */ }
    typing.remove();

    if (!res.ok || !data.reply) {
      addBubble("assistant", data.error || "Something went wrong. Please try again.", "error");
      // Remove the unanswered user message so the history keeps alternating roles
      messages.pop();
      saveMessages();
    } else {
      messages.push({ role: "assistant", content: data.reply });
      saveMessages();
      addBubble("assistant", data.reply);
    }
  } catch (err) {
    typing.remove();
    addBubble("assistant", "Couldn't reach the server. Is it running?", "error");
    messages.pop();
    saveMessages();
  } finally {
    setBusy(false);
  }
}

function clearChat() {
  if (busy) return;
  messages = [];
  saveMessages();
  chatEl.innerHTML = "";
  updateHero();
  inputEl.focus();
}

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    sendMessage(inputEl.value);
  }
});
inputEl.addEventListener("input", autoResize);
sendBtn.addEventListener("click", () => sendMessage(inputEl.value));
clearBtn.addEventListener("click", clearChat);
document.querySelectorAll(".chip").forEach((chip) =>
  chip.addEventListener("click", () => sendMessage(chip.textContent))
);

// Restore saved conversation
messages.forEach((m) => addBubble(m.role, m.content));
updateHero();
inputEl.focus();
