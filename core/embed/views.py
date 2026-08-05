from django.http import HttpResponse

def embed_js(request, website_id):
    js_code = f"""
(function () {{
    const API_URL = "http://127.0.0.1:8000/chat/api/";

    // Chat button
    const button = document.createElement("div");
    button.innerText = "💬 Chat";
    Object.assign(button.style, {{
        position: "fixed",
        bottom: "20px",
        right: "20px",
        background: "#ff7a18",
        color: "#fff",
        padding: "12px 16px",
        borderRadius: "20px",
        cursor: "pointer",
        zIndex: "9999"
    }});

    // Chat box
    const chatBox = document.createElement("div");
    Object.assign(chatBox.style, {{
        position: "fixed",
        bottom: "80px",
        right: "20px",
        width: "300px",
        height: "350px",
        background: "#fff",
        border: "1px solid #ccc",
        borderRadius: "10px",
        display: "none",
        flexDirection: "column",
        zIndex: "9999"
    }});

    chatBox.innerHTML = `
        <div style="padding:10px;background:#ff7a18;color:#fff;">
            ISP Assistant
        </div>
        <div id="messages" style="flex:1;padding:10px;overflow-y:auto;"></div>
        <div style="display:flex;border-top:1px solid #ddd;">
            <input id="msgInput" style="flex:1;padding:8px;" placeholder="Type message..." />
            <button id="sendBtn" style="padding:8px;background:#ff7a18;color:white;">Send</button>
        </div>
    `;

    button.onclick = () => {{
        chatBox.style.display = chatBox.style.display === "none" ? "flex" : "none";
    }};

    chatBox.querySelector("#sendBtn").onclick = async () => {{
        const input = chatBox.querySelector("#msgInput");
        const msg = input.value.trim();
        if (!msg) return;

        const messages = chatBox.querySelector("#messages");

        const userMsg = document.createElement("div");
        userMsg.innerText = msg;
        userMsg.style.textAlign = "right";
        messages.appendChild(userMsg);

        input.value = "";

        try {{
            console.log("Sending message to backend:", msg);

            const res = await fetch(API_URL, {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json"
                }},
                body: JSON.stringify({{
                    message: msg,
                    website_id: "{website_id}"
                }})
            }});

            const data = await res.json();

            const botMsg = document.createElement("div");
            botMsg.innerText = data.reply || "No reply";
            botMsg.style.textAlign = "left";
            messages.appendChild(botMsg);

        }} catch (err) {{
            console.error("Chat error:", err);
        }}
    }};

    document.body.appendChild(button);
    document.body.appendChild(chatBox);
}})();
"""
    return HttpResponse(js_code, content_type="application/javascript")
