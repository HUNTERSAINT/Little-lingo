const session = { level: 1, correct_streak: 0, turns: 0, lesson_index: 0 };
const byId = (id) => document.getElementById(id);
const messageList = byId("messages");

function addMessage(text, sender = "bot") {
  const row = document.createElement("div");
  row.className = `message ${sender}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  // Render text, never user-supplied HTML.
  bubble.textContent = text;
  row.appendChild(bubble);
  messageList.appendChild(row);
  messageList.scrollTop = messageList.scrollHeight;
}

function showProgress(result) {
  Object.assign(session, {
    level: result.level,
    correct_streak: result.correct_streak,
    turns: result.turns,
    lesson_index: result.lesson_index,
  });
  byId("levelName").textContent = `Level ${result.level} · ${result.level_title}`;
  byId("progressBar").style.width = `${result.progress}%`;
  byId("progressText").textContent = result.progress ? `${result.progress}% to the next level` : "Every try counts";
  document.querySelectorAll(".stage-list span").forEach((item, index) => {
    item.classList.toggle("selected", index === result.level - 1);
  });
  byId("lessonPrompt").textContent = result.next_question;
}

async function askPip(rawText) {
  const message = rawText.trim();
  if (!message) return;
  addMessage(message, "user");
  byId("messageInput").value = "";
  const sendButton = document.querySelector(".composer button");
  sendButton.disabled = true;
  const waiting = document.createElement("div");
  waiting.className = "typing";
  waiting.textContent = "Pip is thinking…";
  messageList.appendChild(waiting);
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...session, message }),
    });
    if (!response.ok) throw new Error("The chat request failed");
    const result = await response.json();
    waiting.remove();
    addMessage(result.reply);
    showProgress(result);
  } catch {
    waiting.remove();
    addMessage("I can’t reach our little learning corner right now. Please try again in a moment.");
  } finally {
    sendButton.disabled = false;
    byId("messageInput").focus();
  }
}

byId("chatForm").addEventListener("submit", (event) => {
  event.preventDefault();
  askPip(byId("messageInput").value);
});
document.querySelectorAll("[data-msg]").forEach((button) => {
  button.addEventListener("click", () => askPip(button.dataset.msg));
});
byId("resetBtn").addEventListener("click", () => {
  Object.assign(session, { level: 1, correct_streak: 0, turns: 0, lesson_index: 0 });
  messageList.replaceChildren();
  addMessage("Welcome back. 🌿 We can take this one little step at a time.");
  byId("levelName").textContent = "Level 1 · Little Learner";
  byId("progressBar").style.width = "0";
  byId("progressText").textContent = "Every try counts";
  byId("lessonPrompt").textContent = "Which one is a colour: red or run?";
  document.querySelectorAll(".stage-list span").forEach((item, index) => item.classList.toggle("selected", index === 0));
});
