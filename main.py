import os
import json
import hashlib
import hmac
import time
from fastapi import FastAPI, Request, Response
import httpx
import anthropic

app = FastAPI()
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

APP_ID = os.environ["APP_ID"]
APP_SECRET = os.environ["APP_SECRET"]
VERIFICATION_TOKEN = os.environ.get("APP_VERIFICATION_TOKEN", "")
ENCRYPT_KEY = os.environ.get("APP_ENCRYPT_KEY", "")
BOT_NAME = os.environ.get("BOT_NAME", "Claude")
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

# 简单内存存储对话历史，key = chat_id
conversation_history: dict[str, list] = {}
# 防重放，存已处理的 message_id
processed_messages: set = set()


async def get_tenant_token() -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": APP_ID, "app_secret": APP_SECRET},
        )
        return resp.json()["tenant_access_token"]


async def send_message(chat_id: str, text: str, msg_type: str = "text"):
    token = await get_tenant_token()
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://open.feishu.cn/open-apis/im/v1/messages",
            headers={"Authorization": f"Bearer {token}"},
            params={"receive_id_type": "chat_id"},
            json={
                "receive_id": chat_id,
                "msg_type": "text",
                "content": json.dumps({"text": text}),
            },
        )


def get_claude_reply(chat_id: str, user_text: str) -> str:
    history = conversation_history.setdefault(chat_id, [])
    history.append({"role": "user", "content": user_text})

    # 保留最近 20 条
    if len(history) > 20:
        history = history[-20:]
        conversation_history[chat_id] = history

    response = claude.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=history,
    )
    reply = response.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply


@app.get("/ping")
def ping():
    return "pong"


@app.post("/webhook/event")
async def webhook_event(request: Request):
    body = await request.json()

    # URL 验证
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}

    event = body.get("event", {})
    message = event.get("message", {})
    msg_id = message.get("message_id", "")

    # 防重放
    if msg_id in processed_messages:
        return {"code": 0}
    processed_messages.add(msg_id)

    msg_type = message.get("message_type", "")
    if msg_type != "text":
        return {"code": 0}

    content = json.loads(message.get("content", "{}"))
    text = content.get("text", "").strip()

    # 群聊需要 @机器人
    chat_type = message.get("chat_type", "")
    if chat_type == "group":
        if f"@{BOT_NAME}" not in text and "<at" not in message.get("content", ""):
            return {"code": 0}
        # 去掉 @mention
        import re
        text = re.sub(r"@\S+", "", text).strip()

    if not text:
        return {"code": 0}

    chat_id = message.get("chat_id", "")
    reply = get_claude_reply(chat_id, text)
    await send_message(chat_id, reply)
    return {"code": 0}
