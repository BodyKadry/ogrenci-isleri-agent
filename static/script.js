const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const chatMessages = document.getElementById("chatMessages");
const sendButton = document.getElementById("sendButton");
const suggestionButtons = document.querySelectorAll(".suggestion-button");

let isSending = false;

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  await sendMessage();
});

messageInput.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    await sendMessage();
  }
});

messageInput.addEventListener("input", resizeMessageInput);

suggestionButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    if (isSending) {
      return;
    }

    messageInput.value = button.dataset.question || "";
    resizeMessageInput();
    await sendMessage();
  });
});

async function sendMessage() {
  const userMessage = messageInput.value.trim();

  if (!userMessage || isSending) {
    return;
  }

  setLoadingState(true);
  messageInput.value = "";
  resizeMessageInput();

  addMessage("user", userMessage);
  const loadingMessage = addLoadingMessage();

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userMessage }),
    });

    const data = await parseJsonResponse(response);
    loadingMessage.remove();
    addMessage("assistant", data.reply || "Cevap alınamadı. Lütfen tekrar deneyin.");
  } catch (error) {
    loadingMessage.remove();
    addMessage("assistant", "Sunucuya ulaşılamadı. Lütfen bağlantınızı kontrol edin.");
  } finally {
    setLoadingState(false);
    messageInput.focus();
  }
}

async function parseJsonResponse(response) {
  try {
    return await response.json();
  } catch (error) {
    return {
      reply: response.ok
        ? "Cevap okunamadı. Lütfen tekrar deneyin."
        : "Sunucu beklenmeyen bir hata döndürdü. Lütfen daha sonra tekrar deneyin.",
    };
  }
}

function setLoadingState(loading) {
  isSending = loading;
  sendButton.disabled = loading;
  messageInput.disabled = loading;

  suggestionButtons.forEach((button) => {
    button.disabled = loading;
  });
}

function resizeMessageInput() {
  messageInput.style.height = "auto";
  messageInput.style.height = `${Math.min(messageInput.scrollHeight, 132)}px`;
}

function addMessage(role, text) {
  const messageElement = document.createElement("article");
  messageElement.className = `message ${role}`;

  if (role === "assistant") {
    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = "AI";
    messageElement.appendChild(avatar);
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (role === "assistant") {
    bubble.innerHTML = renderMarkdown(text);
  } else {
    bubble.textContent = text;
  }

  messageElement.appendChild(bubble);
  chatMessages.appendChild(messageElement);
  scrollToBottom();

  return messageElement;
}

function renderMarkdown(text) {
  if (window.marked && window.DOMPurify) {
    try {
      const html = window.marked.parse(text || "", { breaks: true });
      return window.DOMPurify.sanitize(html);
    } catch (error) {
      return fallbackTextToHtml(text);
    }
  }

  return fallbackTextToHtml(text);
}

function fallbackTextToHtml(text) {
  return escapeHtml(text || "").replace(/\n/g, "<br>");
}

function escapeHtml(text) {
  return text.replace(/[&<>"']/g, (character) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#039;",
    };

    return entities[character];
  });
}

function addLoadingMessage() {
  const messageElement = document.createElement("article");
  messageElement.className = "message assistant";

  const avatar = document.createElement("div");
  avatar.className = "message-avatar";
  avatar.setAttribute("aria-hidden", "true");
  avatar.textContent = "AI";

  const bubble = document.createElement("div");
  bubble.className = "bubble bubble-loading";
  bubble.innerHTML = '<span class="typing" aria-label="Cevap yazılıyor"><span></span><span></span><span></span></span>';

  messageElement.appendChild(avatar);
  messageElement.appendChild(bubble);
  chatMessages.appendChild(messageElement);
  scrollToBottom();

  return messageElement;
}

function scrollToBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
