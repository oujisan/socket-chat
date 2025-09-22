import socket

HOST = "0.0.0.0"
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sck:
    sck.bind((HOST, PORT))
    print(f"UDP server listening on {HOST}:{PORT}")

    while True:
        data, addr = sck.recvfrom(1024)
        msg = data.decode().strip()
        print(f"[{addr[0]}:{addr[1]}] {msg}")
