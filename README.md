# 飞书 Claude 机器人

飞书 + Claude API，支持私聊和群聊，多轮对话。

## 部署到 Railway

1. Fork 或 push 本项目到你的 GitHub
2. 去 [railway.app](https://railway.app) 新建项目，选 "Deploy from GitHub repo"
3. 配置环境变量（见下方）
4. 部署完成后拿到域名

## 环境变量

| 变量 | 说明 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic API Key，`sk-ant-xxx` |
| `APP_ID` | 飞书应用 App ID |
| `APP_SECRET` | 飞书应用 App Secret |
| `APP_VERIFICATION_TOKEN` | 飞书事件订阅 Verification Token |
| `APP_ENCRYPT_KEY` | 飞书事件订阅 Encrypt Key（可选） |
| `BOT_NAME` | 机器人名称，默认 `Claude` |
| `CLAUDE_MODEL` | 模型，默认 `claude-sonnet-4-6` |

## 飞书后台配置

1. 去 [飞书开放平台](https://open.feishu.cn/app) 创建应用
2. 开启机器人功能
3. 事件订阅填写：`https://你的域名.railway.app/webhook/event`
4. 订阅以下事件：
   - `im:message.receive_v1`（接收消息）
5. 权限管理勾选：
   - `im:message`
   - `im:message:send_as_bot`
   - `im:chat:readonly`
6. 发布应用

## 验证部署

访问 `https://你的域名.railway.app/ping`，返回 `pong` 说明正常。
