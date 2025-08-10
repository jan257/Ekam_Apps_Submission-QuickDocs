document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("send-btn");
    const queryInput = document.getElementById("query-input");
    const chatBox = document.getElementById("chat-box");

    function addMessage(text, sender) {
        const msg = document.createElement("div");
        msg.classList.add("chat-message", sender === "user" ? "user-message" : "bot-message");
        msg.innerText = text;
        chatBox.appendChild(msg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function sendQuery() {
        const query = queryInput.value.trim();
        if (!query) return;
        
        addMessage(query, "user");
        queryInput.value = "";

        try {
            const res = await fetch("/query", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ nl_query: query })
            });
            const data = await res.json();
            if (data.message) {
                addMessage(data.message, "bot");
            } else {
                addMessage(JSON.stringify(data.results, null, 2), "bot");
            }
        } catch (err) {
            addMessage("Error fetching results.", "bot");
        }
    }

    sendBtn.addEventListener("click", sendQuery);
    queryInput.addEventListener("keypress", e => {
        if (e.key === "Enter") sendQuery();
    });
});
