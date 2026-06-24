console.log("chat.js loaded");

const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-btn");
const chatHistory = document.getElementById("chat-history");
const pdfUpload = document.getElementById("pdf-upload");

let isSending = false;

sendButton.addEventListener("click", sendMessage);


chatInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});

// async, function may paused while waiting (contain async function)
// Function may pause and resume later
async function sendMessage() {
    const message = chatInput.value.trim();

    if (!message || isSending) {
        return;
    }

    isSending = true;
    sendButton.disabled = true;

    addMessage(message, "user");
    chatInput.value = "";

    try {
        const formData = { message: message };

        // Attach extracted PDF text if a file is uploaded
        if (window._extractedPdfText) {
            formData.resume_text = window._extractedPdfText;
        }

        const response = await fetch(window.BACKEND_URL + "/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorBody = await response.text();
            throw new Error(`Server responded with ${response.status}: ${errorBody}`);
        }

        const data = await response.json();

        if (data.reply) {
            addMessage(data.reply, "bot");
        } else {
            addMessage("Unexpected response from server.", "bot");
        }

    } catch (error) {
        console.error(error);
        addMessage("Error talking to backend.", "bot");
    } finally {
        isSending = false;
        sendButton.disabled = false;
    }
}

function addMessage(message, sender) {
    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    if (sender === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("bot-message");
    }

    messageDiv.textContent = message;
    chatHistory.appendChild(messageDiv);

    // Force scroll to bottom when text is added
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

