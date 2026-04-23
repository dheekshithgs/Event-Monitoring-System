import socket
import json
import time
import threading
import tkinter as tk
from tkinter import ttk
from cryptography.fernet import Fernet

HOST = "0.0.0.0"
PORT = 9999

KEY = b'RAqiE3wby4Bw53H-hk03E1RXBbQWRdkAA4oXRCodJjk='
cipher = Fernet(KEY)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

nodes = {}
alerts = {}

heartbeat_log = []
important_log = []

alert_state = {}
status_state = {}

lock = threading.Lock()


def server_loop():
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            event = json.loads(cipher.decrypt(data).decode())

            node = event["node"]
            seq = event.get("seq", 0)
            etype = event["type"]

            with lock:

                if node not in nodes:
                    nodes[node] = {
                        "last_seen": time.time(),
                        "last_seq": seq,
                        "cpu": 0,
                        "ram": 0,
                        "loss": 0
                    }
                    important_log.append(f"{node} REGISTERED")

                else:
                    expected = nodes[node]["last_seq"] + 1
                    gap = seq - expected
                    if gap > 0:
                        nodes[node]["loss"] += gap
                        important_log.append(f"{node} PACKET LOSS x{gap}")

                    nodes[node]["last_seq"] = seq
                    nodes[node]["last_seen"] = time.time()

                if etype == "CPU_UPDATE":
                    nodes[node]["cpu"] = event["value"]
                    important_log.append(f"{node} CPU {event['value']}%")

                elif etype == "RAM_UPDATE":
                    nodes[node]["ram"] = event["value"]
                    important_log.append(f"{node} RAM {event['value']}%")

                elif etype == "HEARTBEAT":
                    heartbeat_log.append(f"{node} heartbeat")

                sev = event.get("severity")
                if sev:
                    prev = alert_state.get(node, "INFO")
                    if sev != prev and sev in ["WARNING", "CRITICAL"]:
                        alerts[node] = alerts.get(node, 0) + 1
                        important_log.append(f"ALERT {node} {etype} {sev}")
                    alert_state[node] = sev

        except Exception as e:
            print("SERVER ERROR:", e)


threading.Thread(target=server_loop, daemon=True).start()


# ================= GUI =================

root = tk.Tk()
root.title("Distributed UDP Monitoring")
root.geometry("1100x600")

tk.Label(root,
         text="Secure Distributed UDP Monitoring Dashboard",
         font=("Arial", 20)).pack(pady=5)

cols = ("Node", "Status", "CPU", "RAM", "Alerts", "Packet Loss")

tree = ttk.Treeview(root, columns=cols, show="headings")

for c in cols:
    tree.heading(c, text=c)
    tree.column(c, width=160)

tree.pack(pady=10)

frame = tk.Frame(root)
frame.pack()

left = tk.Frame(frame)
left.pack(side="left", padx=20)

tk.Label(left, text="Heartbeat Stream").pack()

hb_box = tk.Listbox(left, width=60, height=12)
hb_box.pack()

right = tk.Frame(frame)
right.pack(side="right", padx=20)

tk.Label(right, text="Important Events").pack()

imp_box = tk.Listbox(right, width=60, height=12)
imp_box.pack()


def refresh():
    for r in tree.get_children():
        tree.delete(r)

    now = time.time()

    with lock:
        for node, data in nodes.items():

            status = "ALIVE" if now - data["last_seen"] < 10 else "DOWN"

            prev = status_state.get(node, "UNKNOWN")

            if status != prev:
                if status == "DOWN":
                    important_log.append(f"{node} NODE DOWN")
                elif status == "ALIVE":
                    important_log.append(f"{node} NODE RECOVERED")

                status_state[node] = status

            row = tree.insert("", "end",
                              values=(
                                  node,
                                  status,
                                  data["cpu"],
                                  data["ram"],
                                  alerts.get(node, 0),
                                  data["loss"]
                              ))

            if data["cpu"] > 80 or data["ram"] > 80:
                tree.item(row, tags=("critical",))
            elif data["cpu"] > 50 or data["ram"] > 50:
                tree.item(row, tags=("warn",))
            else:
                tree.item(row, tags=("ok",))

        hb_box.delete(0, tk.END)
        for e in heartbeat_log[-25:]:
            hb_box.insert(tk.END, e)

        imp_box.delete(0, tk.END)
        for e in important_log[-25:]:
            imp_box.insert(tk.END, e)

    root.after(1000, refresh)


tree.tag_configure("critical", background="#ffb3b3")
tree.tag_configure("warn", background="#fff0b3")
tree.tag_configure("ok", background="#ccffcc")

refresh()
root.mainloop()