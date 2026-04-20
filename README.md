cat << 'EOF' > README.md
# Multi-threaded Audio Streaming with Adaptive QoS

## 🎙️ Project Overview
Developed by **Ujwal Sanikam L** and **Ved Mudkavi** [cite: 2], this project is a high-performance audio streaming system built using Python and TCP/IP sockets[cite: 1, 3]. It is designed to handle multiple clients simultaneously while dynamically adjusting audio quality based on real-time network conditions[cite: 348, 356].

## 🚀 Key Features
* **Adaptive Streaming (QoS):** The client monitors the time taken to receive data chunks[cite: 353, 354]. If latency is detected, it signals the server (e.g., "LOW_Q") to adapt the stream[cite: 357, 358].
* **Multi-threaded Architecture:** The server uses a main thread to listen for connections and spawns dedicated worker threads for each client[cite: 219, 220, 221]. This prevents the server from blocking while streaming to multiple users[cite: 213, 216].
* **Flask Web Interface:** Includes a local web UI to browse available `.mp3` files and track download progress.
* **Efficient Buffering:** Uses a 4096-byte chunk size to stream audio without overwhelming system RAM or network bandwidth[cite: 94, 98].
* **Dynamic File Discovery:** The server scans the directory for available files and provides a list to the client upon request.

## 🛠️ Technical Stack
* **Language:** Python 3
* **Networking:** Sockets (TCP/IP) [cite: 3, 32]
* **Concurrency:** `threading` module [cite: 245]
* **Web Framework:** Flask (for Client UI)
* **I/O Multiplexing:** `select` module (for server-side QoS monitoring)

## 📖 Implementation Phases
1. **Phase 1:** Basic TCP Handshake and text communication[cite: 3].
2. **Phase 2:** Single-client file streaming using binary buffers[cite: 92].
3. **Phase 3:** Multi-threaded support for concurrent listeners[cite: 213].
4. **Phase 4:** Adaptive streaming logic and Quality of Service evaluation[cite: 348].

## 🚦 How to Run
1. **Start the Server:**
   \`\`\`bash
   python server.py
   \`\`\`
2. **Start the Client UI:**
   \`\`\`bash
   python client.py
   \`\`\`
3. **Access the Dashboard:** Open your browser and go to \`http://127.0.0.1:5000\`.

EOF
