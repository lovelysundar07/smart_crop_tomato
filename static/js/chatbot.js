// chatbot.js
// Floating Gemini-powered farmer assistant. Has its own EN/TA toggle,
// independent of the page's server-rendered language, so the farmer can
// switch mid-conversation without reloading the page.

(function () {
    const root = document.getElementById("chatbot-root");
    if (!root) return;

    const toggleBtn = document.getElementById("chatbot-toggle");
    const panel = document.getElementById("chatbot-panel");
    const closeBtn = document.getElementById("chatbot-close");
    const langBtn = document.getElementById("chatbot-lang-toggle");
    const messagesEl = document.getElementById("chatbot-messages");
    const typingEl = document.getElementById("chatbot-typing");
    const form = document.getElementById("chatbot-form");
    const input = document.getElementById("chatbot-input");

    let chatLang = panel.dataset.currentLang === "ta" ? "ta" : "en";
    let history = [];

    const STRINGS = {
        en: {
            title: "Farmer Assistant",
            greeting: "Hello! Ask me anything about tomato farming, irrigation, soil, weather or pests.",
            placeholder: "Type your question...",
            send: "Send",
            langBtn: "தமிழ்",
            typing: "Typing...",
        },
        ta: {
            title: "விவசாயி உதவியாளர்",
            greeting: "வணக்கம்! தக்காளி விவசாயம், நீர்ப்பாசனம், மண், வானிலை அல்லது பூச்சிகள் பற்றி என்னிடம் கேளுங்கள்.",
            placeholder: "உங்கள் கேள்வியை தட்டச்சு செய்யவும்...",
            send: "அனுப்பு",
            langBtn: "English",
            typing: "தட்டச்சு செய்கிறது...",
        },
    };

    function applyStrings() {
        const s = STRINGS[chatLang];
        panel.querySelector(".chatbot-title").textContent = "🤖 " + s.title;
        input.placeholder = s.placeholder;
        document.getElementById("chatbot-send-btn").textContent = s.send;
        langBtn.textContent = s.langBtn;
        typingEl.textContent = s.typing;
    }

    function addMessage(text, sender) {
        const bubble = document.createElement("div");
        bubble.className = `chatbot-bubble chatbot-${sender}`;
        bubble.textContent = text;
        messagesEl.appendChild(bubble);
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function openPanel() {
        panel.classList.remove("chatbot-hidden");
        if (messagesEl.children.length === 0) {
            addMessage(STRINGS[chatLang].greeting, "bot");
        }
        input.focus();
    }

    toggleBtn.addEventListener("click", () => {
        if (panel.classList.contains("chatbot-hidden")) {
            openPanel();
        } else {
            panel.classList.add("chatbot-hidden");
        }
    });

    closeBtn.addEventListener("click", () => panel.classList.add("chatbot-hidden"));

    langBtn.addEventListener("click", () => {
        chatLang = chatLang === "en" ? "ta" : "en";
        applyStrings();
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const message = input.value.trim();
        if (!message) return;

        addMessage(message, "user");
        input.value = "";
        typingEl.style.display = "block";
        messagesEl.scrollTop = messagesEl.scrollHeight;

        try {
            const res = await fetch("/api/chatbot", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message, lang: chatLang, history }),
            });
            const data = await res.json();
            typingEl.style.display = "none";

            const reply = data.reply || (chatLang === "ta"
                ? "மன்னிக்கவும், பதிலளிக்க முடியவில்லை."
                : "Sorry, I couldn't get a reply.");
            addMessage(reply, "bot");

            history.push({ role: "user", text: message });
            history.push({ role: "model", text: reply });
            if (history.length > 12) history = history.slice(-12);
        } catch (err) {
            typingEl.style.display = "none";
            addMessage(chatLang === "ta" ? "பிழை ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்." : "Something went wrong. Please try again.", "bot");
            console.error(err);
        }
    });

    applyStrings();
})();
