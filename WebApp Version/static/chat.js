const socket = io({
    withCredentials: true
});

socket.on("connect", () => console.log("Socket connected"));
socket.on("disconnect", () => console.log("Socket disconnected"));

// Used to have bot display msg immedietly
socket.on("bot_message", (msg) => {
    addMessage("Bot", msg);
});

// Trigger /start when page loads
window.addEventListener("DOMContentLoaded", () => {
    fetch("/start", { credentials: "same-origin" });

    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "light") {
        document.body.classList.add("light");
        sunIcon.style.display = "block";
        moonIcon.style.display = "none";
    } else {
        sunIcon.style.display = "none";
        moonIcon.style.display = "block";
    }
});

function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value;
    input.value = "";
    addMessage("You", message);

    fetch("/chat", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })
    })

    .then(res => res.json())
    .then(data => addMessage("Bot", data.reply));
}

function addMessage(sender, text) {
    const chatBox = document.getElementById("chat-box");
    const div = document.createElement("div");
    div.className = sender.toLowerCase();
    div.innerText = `${sender}: ${text}`;
    chatBox.appendChild(div);

    // Smooth scroll to bottom
    chatBox.scrollTo({
        top: chatBox.scrollHeight,
        behavior: "smooth"
    });
}

function toggleInfo() {
    const info = document.getElementById("info-text");
    info.style.display = info.style.display === "block" ? "none" : "block";
}

// Dark mode toggle logic:
const toggleBtn = document.getElementById("theme-toggle");
const sunIcon = document.getElementById("sun");
const moonIcon = document.getElementById("moon");

function toggleTheme() {
    document.body.classList.toggle("light");

    const isLight = document.body.classList.contains("light");

    // Switch which icon is visible
    sunIcon.style.display = isLight ? "block" : "none";
    moonIcon.style.display = isLight ? "none" : "block";

    localStorage.setItem("theme", isLight ? "light" : "dark");
}