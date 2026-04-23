import socket
import json
import time
import psutil
import platform
from cryptography.fernet import Fernet

SERVER_IP = "10.1.22.249"
PORT = 9999

KEY = b'RAqiE3wby4Bw53H-hk03E1RXBbQWRdkAA4oXRCodJjk='
cipher = Fernet(KEY)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
if sock:
	print("Connecting to Server...")
	
NODE = platform.node()

seq = 0
last_cpu = 0
last_ram = 0


def classify(v):
    if v > 80:
        return "CRITICAL"
    if v > 50:
        return "WARNING"
    return "INFO"


def send(event):
    global seq
    event["seq"] = seq
    seq += 1

    msg = cipher.encrypt(json.dumps(event).encode())
    sock.sendto(msg, (SERVER_IP, PORT))


send({
    "node": NODE,
    "type": "REGISTER"
})


while True:

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    new_cpu_sev = classify(cpu)
    old_cpu_sev = classify(last_cpu)

    if abs(cpu - last_cpu) > 10 or new_cpu_sev != old_cpu_sev:
        send({
            "node": NODE,
            "type": "CPU_UPDATE",
            "value": cpu,
            "severity": new_cpu_sev
        })
        last_cpu = cpu

    new_ram_sev = classify(ram)
    old_ram_sev = classify(last_ram)

    if abs(ram - last_ram) > 10 or new_ram_sev != old_ram_sev:
        send({
            "node": NODE,
            "type": "RAM_UPDATE",
            "value": ram,
            "severity": new_ram_sev
        })
        last_ram = ram

    send({
        "node": NODE,
        "type": "HEARTBEAT"
    })

    time.sleep(3)
