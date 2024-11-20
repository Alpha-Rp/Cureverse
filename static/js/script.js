var socket = io();
var loadingIndicator = document.getElementById("loading-indicator");
var chatBox = document.getElementById("chat-box");

// Function to load chat history from localStorage
function loadChatHistory() {
  var chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];
  chatHistory.forEach(item => {
    addMessage(item.type, item.message, false);
  });
}

// Function to save chat history to localStorage
function saveChatHistory(type, message) {
  var chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];
  chatHistory.push({ type: type, message: message });
  localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
}

// Function to clear chat history
function clearChatHistory() {
  localStorage.removeItem("chatHistory");
  chatBox.innerHTML = "";
  addMessage("bot", "Chat history has been cleared. How can I assist you today?");
}

// Function to send user message
function sendMessage() {
  var userInput = document.getElementById("user-input");
  var message = userInput.value.trim();

  if (message !== "") {
    addMessage("user", message);
    saveChatHistory("user", message);

    loadingIndicator.style.display = "block"; // Show loading indicator

    socket.emit("send_message", { message: message }); // Send message to server
    userInput.value = ""; // Clear input field
  }
}

// Listen for messages from the server
socket.on("receive_message", function (response) {
  loadingIndicator.style.display = "none"; // Hide loading indicator
  addMessage("bot", response.reply); // Use response.reply to get the bot's message
  saveChatHistory("bot", response.reply); // Save bot message to chat history
});

// Function to handle errors
function handleError(errorMessage) {
  loadingIndicator.style.display = "none"; // Hide loading indicator
  addMessage("error", errorMessage);
  saveChatHistory("error", errorMessage);
}

// Function to add messages to the chat
function addMessage(type, message, save = true) {
  var messageDiv = document.createElement("div");
  messageDiv.className =
    "message " +
    (type === "user"
      ? "user-message"
      : type === "error"
      ? "error-message"
      : "bot-message");
  messageDiv.textContent = message;

  if (type === "bot") {
    var feedbackDiv = document.createElement("div");
    feedbackDiv.className = "feedback-buttons";

    var helpfulButton = document.createElement("button");
    helpfulButton.textContent = "Helpful";
    helpfulButton.className = "feedback-button helpful";
    helpfulButton.onclick = function () {
      sendFeedback("Helpful", message);
    };

    var notHelpfulButton = document.createElement("button");
    notHelpfulButton.textContent = "Not Helpful";
    notHelpfulButton.className = "feedback-button not-helpful";
    notHelpfulButton.onclick = function () {
      sendFeedback("Not Helpful", message);
    };

    feedbackDiv.appendChild(helpfulButton);
    feedbackDiv.appendChild(notHelpfulButton);
    messageDiv.appendChild(feedbackDiv);
  }

  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight; // Scroll to the bottom of the chat

  if (save) {
    saveChatHistory(type, message);
  }
}

// Function to send feedback to the server
function sendFeedback(feedback, message) {
  socket.emit("send_feedback", { feedback: feedback, message: message });
  alert(`Thank you for your feedback: "${feedback}" on the message: "${message}"`);
}

// Enter key to send message
document
  .getElementById("user-input")
  .addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

// Load chat history when the page loads
window.onload = function () {
  loadChatHistory();
};

// Add a clear chat history button functionality
document
  document
    .getElementById("clear-history")
    .addEventListener("click", clearChatHistory);