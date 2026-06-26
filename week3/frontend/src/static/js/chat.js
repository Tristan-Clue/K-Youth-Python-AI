// Importing pdf.js to module
import * as pdfjsLib from "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.min.mjs"

pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.8.69/pdf.worker.min.mjs";


const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-btn");
const chatHistory = document.getElementById("chat-history");
const pdfUpload = document.getElementById("pdf-upload");

let isSending = false;
let pendingPdfFile = null;
let storedResumeText = null;


sendButton.addEventListener("click", sendMessage);

// --- PDF Upload Handler ---
// Stores the raw file; extraction happens on send to avoid unnecessary work

pdfUpload.addEventListener("change", function(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== "application/pdf") {
        addMessage("Please upload a PDF file.", "bot");
        pdfUpload.value = "";
        return;
    }

    pendingPdfFile = file;
    addMessage(`PDF selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB). Click Send to attach.`, "bot");
});

async function extractPdfText(arrayBuffer) {
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let fullText = "";

    for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items.map(item => item.str).join(" ");
        fullText += pageText + "\n";
    }

    return fullText.trim();
}


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

    // Extract PDF text at send time if a file was selected
    let pdfTextToSend = null;
    if (pendingPdfFile) {
        try {
            const arrayBuffer = await pendingPdfFile.arrayBuffer();
            pdfTextToSend = await extractPdfText(arrayBuffer);
            storedResumeText = pdfTextToSend;
            addMessage(`PDF attached: ${pendingPdfFile.name} (${pdfTextToSend.length} characters)`, "bot");
        } catch (error) {
            console.error("PDF extraction failed:", error);
            addMessage("Failed to read PDF. Message sent without resume.", "bot");
        }
        pendingPdfFile = null;
        pdfUpload.value = "";
    }

    try {
        const formData = { message: message };

        // Attach newly extracted PDF text if present
        if (pdfTextToSend) {
            formData.resume_text = pdfTextToSend;
        }

        // Include stored resume text so the backend retains context
        if (storedResumeText && !formData.resume_text) {
            formData.resume_text = storedResumeText;
        }

        const response = await fetch("/api/chat", {
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

