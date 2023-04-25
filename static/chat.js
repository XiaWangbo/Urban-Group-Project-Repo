const form = document.getElementById("chat-form");
const chatMessages = document.querySelector(".chat-messages");
const questionInput = document.getElementById("question");

form.addEventListener("submit", (event) => {
    event.preventDefault();

    const question = questionInput.value;
    const pdfInput = document.getElementById("pdf");
    const formData = new FormData();
    formData.append("question", question);

    if (pdfInput.files.length > 0) {
        formData.append("pdf", pdfInput.files[0]);
    }

    const userMessage = document.createElement("div");
    userMessage.classList.add("user-message");
    userMessage.innerText = question;
    chatMessages.appendChild(userMessage);

    fetch("/ask", {
        method: "POST",
        body: formData,
    })
        .then((response) => response.json())
        .then((data) => {
            const botMessage = document.createElement("div");
            botMessage.classList.add("bot-message");
            botMessage.innerText = data.answer || "I'm sorry, I couldn't find an answer.";
            chatMessages.appendChild(botMessage);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });

    questionInput.value = "";
});


