// Initialize marked for markdown parsing
if (typeof marked !== "undefined") {
  marked.setOptions({
    breaks: true,
    gfm: true,
    headerIds: false,
    sanitize: false,
  });
} else {
  console.warn("Marked library not loaded. Markdown parsing will be disabled.");
  // Create a simple fallback if marked is not available
  window.marked = {
    parse: function (text) {
      return text;
    },
  };
}

// Main app class
class CureVerseApp {
  constructor() {
    this.socket = io();
    this.chatArea = document.getElementById("chat-area");
    this.chatForm = document.getElementById("chat-form");
    this.chatInput = document.getElementById("chat-input");
    this.sendBtn = document.getElementById("send-btn");
    this.typingIndicator = document.getElementById("typing-indicator");
    this.suggestionChips = document.querySelectorAll(".suggestion-chip");
    this.clearHistoryBtn = document.getElementById("clear-history");
    this.toggleSidebarBtn = document.getElementById("toggle-sidebar");
    this.sidebar = document.querySelector(".sidebar");
    this.messageHistory = [];

    // Clear any existing chat history from localStorage
    localStorage.removeItem("cureverse_chat_history");

    this.initEventListeners();
    this.initSocketListeners();

    // Clear the chat area
    this.chatArea.innerHTML = "";

    // Always send a welcome message on startup
    this.sendWelcomeMessage();
  }

  initEventListeners() {
    // Send message on form submit
    this.chatForm.addEventListener("submit", e => {
      e.preventDefault();
      this.sendMessage();
    });

    // Send message on button click
    this.sendBtn.addEventListener("click", () => {
      this.sendMessage();
    });

    // Handle suggestion chips
    this.suggestionChips.forEach(chip => {
      chip.addEventListener("click", () => {
        this.sendSuggestion(chip.textContent);
      });
    });

    // Clear chat history
    if (this.clearHistoryBtn) {
      this.clearHistoryBtn.addEventListener("click", () => {
        this.clearChatHistory();
      });
    }

    // Toggle sidebar on mobile
    if (this.toggleSidebarBtn) {
      this.toggleSidebarBtn.addEventListener("click", () => {
        this.sidebar.classList.toggle("sidebar-open");
      });
    }
  }

  initSocketListeners() {
    // Listen for messages from the server
    this.socket.on("receive_message", response => {
      // Ensure typing indicator shows for at least 1.5 seconds
      const minDelay = 1500; // 1.5 seconds
      const startTime = this.typingStartTime || Date.now();
      const elapsed = Date.now() - startTime;
      const remainingDelay = Math.max(0, minDelay - elapsed);

      setTimeout(() => {
        this.hideTypingIndicator();
        this.appendBotMessage(response);
      }, remainingDelay);
    });
  }

  sendMessage() {
    const message = this.chatInput.value.trim();
    if (message) {
      this.appendUserMessage(message); // This already saves to history
      this.showTypingIndicator();
      this.socket.emit("send_message", { message });
      this.chatInput.value = "";
    }
  }

  sendSuggestion(suggestion) {
    this.chatInput.value = suggestion;
    this.sendMessage();
  }

  appendUserMessage(message, saveToHistory = true) {
    const messageElement = this.createMessageElement("user", message);
    this.chatArea.appendChild(messageElement);
    this.scrollToBottom();

    // Only save to history if specified
    if (saveToHistory) {
      this.saveChatHistory("user", message);
    }
  }

  appendBotMessage(response, saveToHistory = true) {
    // Handle both string messages and response objects
    if (typeof response === "string") {
      response = {
        message: response,
        causes: [],
        consultationAdvice: "",
        ayurvedicRemedies: [],
        dietPlan: [],
      };
    }

    const messageElement = this.createMessageElement("bot", response.message);
    this.chatArea.appendChild(messageElement);
    this.scrollToBottom();

    // If we have medical information, display it
    if (response.causes && response.causes.length > 0) {
      this.appendMedicalCard(response);
    }

    // Only save to history if specified
    if (saveToHistory) {
      this.saveChatHistory("bot", response);
    }
  }

  createMessageElement(type, content) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `chat-message message-${type}`;

    const avatarDiv = document.createElement("div");
    avatarDiv.className = "message-avatar";

    if (type === "bot") {
      avatarDiv.innerHTML = '<i class="fas fa-robot"></i>';
    } else {
      avatarDiv.innerHTML = '<i class="fas fa-user"></i>';
    }

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const textDiv = document.createElement("div");
    textDiv.className = "message-text";

    // Use markdown for bot messages
    if (type === "bot") {
      textDiv.innerHTML = marked.parse(content);
    } else {
      textDiv.textContent = content;
    }

    const timeDiv = document.createElement("div");
    timeDiv.className = "message-time";
    timeDiv.textContent = this.formatTime(new Date());

    contentDiv.appendChild(textDiv);
    contentDiv.appendChild(timeDiv);

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);

    return messageDiv;
  }

  appendMedicalCard(response) {
    const cardDiv = document.createElement("div");
    cardDiv.className = "medical-info-card";

    const cardHeader = document.createElement("div");
    cardHeader.className = "card-header";

    const cardTitle = document.createElement("div");
    cardTitle.className = "card-title";
    cardTitle.textContent = "Medical Information";

    cardHeader.appendChild(cardTitle);

    const cardBody = document.createElement("div");
    cardBody.className = "card-body";

    // Causes Section
    if (response.causes && response.causes.length > 0) {
      const causesSection = this.createInfoSection(
        "Possible Causes",
        "fa-circle-info",
        response.causes
      );
      cardBody.appendChild(causesSection);
    }

    // Consultation Advice
    if (response.consultationAdvice) {
      const consultSection = this.createInfoSection(
        "Medical Advice",
        "fa-user-doctor",
        [response.consultationAdvice]
      );
      cardBody.appendChild(consultSection);
    }

    // Ayurvedic Remedies
    if (response.ayurvedicRemedies && response.ayurvedicRemedies.length > 0) {
      const remediesSection = this.createInfoSection(
        "Ayurvedic Remedies",
        "fa-mortar-pestle",
        response.ayurvedicRemedies
      );
      cardBody.appendChild(remediesSection);
    }

    // Diet Plan
    if (response.dietPlan && response.dietPlan.length > 0) {
      const dietSection = this.createInfoSection(
        "Diet Recommendations",
        "fa-utensils",
        response.dietPlan
      );
      cardBody.appendChild(dietSection);
    }

    cardDiv.appendChild(cardHeader);
    cardDiv.appendChild(cardBody);

    this.chatArea.appendChild(cardDiv);
    this.scrollToBottom();
  }

  createInfoSection(title, icon, items) {
    const section = document.createElement("div");
    section.className = "info-section";

    const titleDiv = document.createElement("div");
    titleDiv.className = "info-title";
    titleDiv.innerHTML = `<i class="fas ${icon}"></i> ${title}`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "info-content";

    const list = document.createElement("ul");
    list.className = "info-list";

    items.forEach(item => {
      const listItem = document.createElement("li");
      listItem.textContent = item;
      list.appendChild(listItem);
    });

    contentDiv.appendChild(list);
    section.appendChild(titleDiv);
    section.appendChild(contentDiv);

    return section;
  }

  showTypingIndicator() {
    this.typingStartTime = Date.now();
    this.typingIndicator.style.display = "block";
    this.scrollToBottom();
  }

  hideTypingIndicator() {
    this.typingIndicator.style.display = "none";
  }

  scrollToBottom() {
    this.chatArea.scrollTop = this.chatArea.scrollHeight;
  }

  formatTime(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  saveChatHistory(type, content) {
    const historyItem = {
      type,
      content,
      timestamp: new Date().toISOString(),
    };

    this.messageHistory.push(historyItem);
    localStorage.setItem(
      "cureverse_chat_history",
      JSON.stringify(this.messageHistory)
    );
  }

  loadChatHistory() {
    const savedHistory = localStorage.getItem("cureverse_chat_history");
    if (savedHistory) {
      try {
        this.messageHistory = JSON.parse(savedHistory);

        // Only load the last 20 messages to prevent overloading
        const recentMessages = this.messageHistory.slice(-20);

        if (recentMessages.length > 0) {
          recentMessages.forEach(item => {
            if (item.type === "user") {
              this.appendUserMessage(item.content, false); // Don't save to history again
            } else if (item.type === "bot") {
              this.appendBotMessage(item.content, false); // Don't save to history again
            }
          });

          this.hasLoadedHistory = true;
          return true; // History was loaded
        }
      } catch (error) {
        console.error("Error loading chat history:", error);
        this.clearChatHistory();
      }
    }

    return false; // No history was loaded
  }

  clearChatHistory() {
    localStorage.removeItem("cureverse_chat_history");
    this.messageHistory = [];
    this.chatArea.innerHTML = "";
    this.sendWelcomeMessage();
  }

  sendWelcomeMessage() {
    const welcomeResponse = {
      message:
        "# 🌿 Welcome to CureVerse Ayurvedic Assistant\n\nI'm your AI-powered Ayurvedic health guide. I can help you with:\n\n* **Natural remedies** for common health concerns\n* **Ayurvedic approaches** to wellness and balance\n* **Dosha-specific advice** for your unique constitution\n* **Seasonal health tips** based on Ayurvedic principles\n\nHow can I assist you with your health journey today?",
      causes: [],
      consultationAdvice: "",
      ayurvedicRemedies: [],
      dietPlan: [],
    };

    this.appendBotMessage(welcomeResponse);
  }

  // Helper function to determine if quick actions should be shown
  shouldShowQuickActions(response) {
    // Show quick actions if we have medical information or specific response types
    return (
      (response.causes && response.causes.length > 0) ||
      (response.ayurvedicRemedies && response.ayurvedicRemedies.length > 0) ||
      response.matchedSymptom
    );
  }
}

// Initialize the app when the DOM is loaded
let app;
document.addEventListener("DOMContentLoaded", () => {
  app = new CureVerseApp();
});

// Global function for clearing chat history (called from sidebar)
function clearChatHistory() {
  if (app) {
    app.clearChatHistory();
  }
}

// Logout function
function logout() {
  fetch("/logout", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(response => {
      if (response.ok) {
        window.location.href = "/";
      }
    })
    .catch(error => {
      console.error("Error during logout:", error);
    });
}
