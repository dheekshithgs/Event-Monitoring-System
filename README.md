# Distributed UDP Network Event Monitoring System

A lightweight distributed monitoring system where multiple nodes detect system events (CPU/RAM thresholds, latency, heartbeat) and send them to a centralized server using UDP.

---

## 🚀 Features

- Multi-client monitoring over WiFi
- UDP-based communication (low overhead)
- Application-layer encryption (Fernet)
- Sequence numbers for packet tracking
- Packet loss detection (basic)
- Edge filtering (reduces redundant alerts)
- Heartbeat (node liveness detection)
- Alert classification (INFO / WARNING / CRITICAL)
- Live CLI dashboard

---

## 📡 Architecture

```text
          +---------+
          | NODE 1  |
          +---------+
                \
                 \
+---------+                   +----------------------+
| NODE 2  |----- UDP  ------> | MONITORING SERVER    |
+---------+                   +----------------------+
                 /
                /
          +---------+
          | NODE 3  |
          +---------+
```
---

## ⚙️ Tech Stack

- Python 3
- socket (UDP)
- psutil
- cryptography (Fernet)

---

## 📦 Installation

```bash
git clone https://github.com/your-username/udp-monitoring-system.git
cd udp-monitoring-system
pip install psutil cryptography
```
## ▶️ Running the Project

### 1. Install Dependencies
Run on all machines (server and nodes):
```bash
pip install psutil cryptography
```
---

### 2. Configure Encryption Key
Generate a key once:

from cryptography.fernet import Fernet
print(Fernet.generate_key())
Copy the generated key into both `server.py` and `node.py`:

KEY = b'YOUR_SHARED_KEY'

⚠️ Important: The key must be identical on server and all nodes.

---

### 3. Start the Server

On the server machine:
python3 server.py

Expected output:

=== DISTRIBUTED MONITORING SERVER ===
The server will now wait for incoming UDP packets.

---

### 4. Get Server IP Address

Run on server:
```bash
ip a
```
Look for your WiFi/LAN IP (example):
192.168.1.8

---

### 5. Configure Node

In `node.py`, update:

SERVER_IP = "192.168.1.8"
REPLACE with your ACTUAL SERVER IP.

---

### 6. Run Node(s)

On one or more machines:
```bash
python3 node.py
```
You can:
- run on multiple laptops (same WiFi)
- or open multiple terminals on same system

---

## 🔍 What to Expect
When nodes start, the server will show:
[NEW NODE] node1 connected from 192.168.x.x  
node1 registered  
Then periodic updates:

node1 | CPU_UPDATE | WARNING | 55%    
Every few seconds, dashboard:
```text
====== SYSTEM STATUS ======  
node1 -> ALIVE | Alerts: 3  
node2 -> DOWN  | Alerts: 1  
===========================  
```
---

## 🧠 What the System Does

Each node:
- monitors CPU and RAM
- sends updates only when values change (edge filtering)
- sends heartbeat signals
- measures latency (ping–pong)
- attaches sequence numbers for tracking

Server:
- decrypts UDP packets
- tracks active nodes
- detects packet loss
- aggregates alerts
- prints system status

---

## ⚠️ Important Notes

### UDP Behavior
- No delivery guarantee
- Packets may be lost or out of order
- Sequence numbers help detect loss

---

### WiFi Limitation
Some networks (especially college WiFi) block device-to-device communication.

If it doesn't work:
- try mobile hotspot
- use same LAN
- test on localhost

---

### Firewall
Allow UDP on server:
```bash
sudo ufw allow 9999/udp
```
---

### No Output?
Check:
- correct SERVER_IP
- both devices on same network
- ping SERVER_IP works
- encryption key matches
- thresholds not too high

---

### Demo Tip
Lower threshold for testing:
if abs(cpu - last_cpu) > 2
Otherwise system may appear inactive.

---

## 📌 Summary

- Start server first  
- Set correct IP and key  
- Run nodes  
- Observe distributed monitoring over UDP  
