
import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

API_KEY = os.environ.get("OPENAI_API_KEY")
CREATOR = os.environ.get("CREATOR_NAME", "Mtengenezaji wa KENYA AI")
MODEL = os.environ.get("AI_MODEL", "gpt-4.1-mini")

client = OpenAI(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = f"""
Wewe ni KENYA AI, akili bandia binafsi iliyoundwa na {CREATOR}.

UTAMBULISHO:
- Jina lako ni KENYA AI.
- Mtengenezaji wako ni {CREATOR}.
- Mheshimu mtengenezaji wako.
- Usidai kumjua mtengenezaji zaidi ya taarifa alizokupa.

UWEZO:
- Jibu maswali ya sayansi, hisabati na elimu.
- Fundisha teknolojia, kompyuta na programming.
- Eleza historia, jiografia na ulimwengu.
- Saidia biashara, ubunifu na utafiti.
- Zungumza Kiswahili na Kiingereza.
- Saidia kuchambua mawazo na kutatua matatizo.
- Toa majibu yaliyo wazi na yenye mifano.

KANUNI:
- Jibu kwa lugha ambayo mtumiaji ametumia.
- Kama hujui jambo, sema ukweli.
- Usitengeneze taarifa za uongo.
- Usidai kuwa umefanya utafutaji wa mtandao
  ikiwa hujafanya.
- Tumia mazungumzo yaliyotangulia kama muktadha.
- Msaidie mtumiaji kujifunza hatua kwa hatua.

LENGO:
Kuwa msaidizi mwenye maarifa mengi, ubunifu,
uelewa na uwezo wa kusaidia watu duniani.
"""

HTML = """
<!DOCTYPE html>
<html lang="sw">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KENYA AI</title>
<style>
body {
    margin:0;
    background:#07111f;
    color:white;
    font-family:Arial,sans-serif;
}
header {
    background:#10243b;
    padding:20px;
    text-align:center;
    border-bottom:1px solid #24415f;
}
header h1 {color:#00d9ff;margin:0;}
header p {color:#a9c5dc;}
#chat {
    max-width:800px;
    margin:auto;
    padding:15px;
    height:65vh;
    overflow-y:auto;
}
.msg {
    padding:13px;
    margin:12px 0;
    border-radius:12px;
    line-height:1.6;
    white-space:pre-wrap;
}
.user {background:#174b71;margin-left:12%;}
.ai {background:#172a40;margin-right:12%;}
footer {
    position:fixed;
    bottom:0;
    left:0;
    right:0;
    background:#10243b;
    padding:12px;
}
.area {
    max-width:800px;
    margin:auto;
    display:flex;
    gap:8px;
}
textarea {
    flex:1;
    padding:13px;
    border-radius:10px;
    border:0;
    resize:none;
    font-size:16px;
}
button {
    background:#00bde8;
    color:#00131e;
    border:0;
    padding:12px 18px;
    border-radius:10px;
    font-weight:bold;
}
</style>
</head>
<body>
<header>
<h1>KENYA AI</h1>
<p>Akili yako. Maarifa ya ulimwengu.</p>
</header>
<div id="chat"></div>
<footer>
<div class="area">
<textarea id="question" rows="2"
placeholder="Uliza KENYA AI swali..."></textarea>
<button onclick="send()">TUMA</button>
</div>
</footer>
<script>
const chat = document.getElementById("chat");
const input = document.getElementById("question");
let history = JSON.parse(localStorage.getItem("kenya_history") || "[]");

function show(role, content) {
    const div = document.createElement("div");
    div.className = "msg " + role;
    div.textContent = content;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

history.forEach(m => show(
    m.role === "user" ? "user" : "ai", m.content
));

if (!history.length) {
    show("ai", "Karibu! Mimi ni KENYA AI. Nikupe msaada gani leo?");
}

async function send() {
    const q = input.value.trim();
    if (!q) return;

    input.value = "";
    show("user", q);

    history.push({role:"user", content:q});
    const loading = document.createElement("div");
    loading.className = "msg ai";
    loading.textContent = "KENYA AI inafikiria...";
    chat.appendChild(loading);

    try {
        const response = await fetch("/chat", {
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({
                message:q,
                history:history.slice(-20)
            })
        });

        const data = await response.json();
        loading.remove();

        if (!response.ok) {
            throw new Error(data.error || "Hitilafu imetokea.");
        }

        show("ai", data.reply);
        history.push({role:"assistant", content:data.reply});
        history = history.slice(-40);
        localStorage.setItem("kenya_history", JSON.stringify(history));

    } catch (error) {
        loading.textContent = "Hitilafu: " + error.message;
    }
}

input.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        send();
    }
});
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "name": "KENYA AI",
        "api_configured": bool(client)
    })

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({
            "error": "OPENAI_API_KEY haijawekwa kwenye Render."
        }), 500

    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    history = data.get("history", [])

    if not message:
        return jsonify({"error": "Andika swali kwanza."}), 400

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for item in history[-20:]:
        role = item.get("role")
        content = item.get("content", "")

        if role in ("user", "assistant") and isinstance(content, str):
            messages.append({
                "role": role,
                "content": content[:12000]
            })

    try:
        result = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        answer = result.choices[0].message.content

        return jsonify({
            "name": "KENYA AI",
            "reply": answer or "Samahani, jaribu tena."
        })

    except Exception as e:
        app.logger.exception("KENYA AI error")
        return jsonify({
            "error": "Imeshindwa kuwasiliana na AI. Angalia API key, model na logs za Render."
        }), 500

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
)
                       
