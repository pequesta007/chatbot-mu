document.addEventListener("DOMContentLoaded", function () {
    const chatbot = document.getElementById("chatbot-container");

    chatbot.innerHTML = `
        <div id="chat-header">Chatbot PDF</div>
        <div id="chat-body"></div>
        <input type="text" id="chat-input" placeholder="Escribe tu pregunta...">
    `;

    document.getElementById("chat-input").addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            let question = this.value;
            fetch("/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question: question })
            })
            .then(response => response.json())
            .then(data => {
                let chatBody = document.getElementById("chat-body");
                chatBody.innerHTML += `<p><strong>Tú:</strong> ${question}</p>`;
                chatBody.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
                this.value = "";
            });
        }
    });
});
