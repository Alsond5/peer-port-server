# WebRTC Signaling Server for P2P File Transfers

A lightweight and scalable WebSocket-based signaling server built with **FastAPI** for establishing **peer-to-peer (P2P)** connections using **WebRTC**. This signaling server is designed to support **file transfer applications** where actual file data is transferred directly between peers — without passing through any server.

## ✨ Features

- **Pure P2P**: No file data is stored or proxied through the server.
- **WebSocket Signaling**: Fast and efficient signaling channel for WebRTC offer/answer and ICE candidates.
- **Room Management**: Dynamically creates and manages rooms with unique IDs.
- **Rate Limiting**: Prevents abusive clients from overloading the system.
- **Connection Cleanup**: Automatically detects and removes stale or disconnected peers.
- **Monitoring-Ready**: Exposes endpoints for basic health checks and metrics integration.

## 🛠 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/)
- [WebSocket](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- Python 3.9+
- Asynchronous architecture with `asyncio`

---

## 📦 Installation

```bash
git clone https://github.com/Alsond5/peer-port-server.git
cd peer-port-server
pip install -r requirements.txt
```

> Note: Make sure you are using Python 3.9 or higher.

---


## 🚀 Running the Server

```bash
fastapi dev app/main.py
```

By default, the server will start on `http://localhost:8000`.

---

## 🔌 WebSocket Endpoint

### URL:
```
ws://<server-address>/signal
```

### Supported Message Types:

| Type         | Description                          |
|--------------|--------------------------------------|
| `join`       | Join a room with a given share ID    |
| `ready`      | Notify that peer is ready to connect |
| `offer`      | WebRTC SDP offer                     |
| `answer`     | WebRTC SDP answer                    |
| `candidate`  | ICE candidate                        |
| `disconnect` | Graceful disconnect                  |

All messages are expected in the following format:

```json
{
  "type": "string",
  "payload": {
    payload_data
  }
}
```

---

## 🧠 Architecture

The server acts **only as a signaling medium** to help two WebRTC clients find each other and exchange metadata (SDP & ICE). File transfers happen directly between peers over WebRTC’s `DataChannel`.

```
[Client A] ←→ [Signaling Server (WebSocket)] ←→ [Client B]
              |                           |
              |-------- (SDP / ICE) ------|
                      (No file data!)
```

---

## 🔐 Security & Production Notes

- Consider replacing `allow_origins=["*"]` with specific domains.
- Enable TLS/SSL when deploying to production.
- Use Docker for containerized deployments.
- Add persistent logging and error monitoring (e.g. Sentry, Prometheus).

---

## 👨‍💻 Author

Developed by [@Alsond5](https://github.com/Alsond5) as a backend component for a P2P file-sharing WebRTC app.

---

## 📄 License

MIT License. See [LICENSE](./LICENSE) for details.