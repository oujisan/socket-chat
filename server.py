import socket
import datetime as dt
import threading

HOST = '0.0.0.0'
PORT = 8888

RESET = "\033[0m"
GRAY  = "\033[90m" 
CYAN  = "\033[96m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"

clients = []
clients_lock = threading.Lock()

def get_time_now():
    return dt.datetime.now().strftime('%d-%m-%Y %H:%M:%S')   

def get_ip_addr():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sck:
        try:
            sck.connect(('8.8.8.8', 80))
            ip = sck.getsockname()[0]
        except:
            ip = '127.0.0.1'
    return ip

def prompt(conn, client_ip, enter=False):
    conn.sendall(f"{'\n' if enter else ''}{YELLOW}{client_ip}> {RESET}".encode())

def broadcast(message, sender):
    with clients_lock:
        for conn, addr in clients:
            try:
                if conn == sender:
                    continue
                conn.sendall(message.encode())
            except:
                continue
        for conn, addr in clients:
            if conn == sender:
                continue
            ip = addr[0]
            prompt(conn, ip, enter=True)

def client(conn, addr):
    client_ip, client_port = addr
    with clients_lock:
        clients.append((conn, addr))
        
    notice_client_new = f"\n{GREEN}[+] Client {client_ip}:{client_port} connected {RESET} ({len(clients)} online)"
    snotice_client_new = f"{GREEN}[{get_time_now()}] Client {client_ip}:{client_port} connected {RESET} ({len(clients)} online)"
    print(snotice_client_new)
    
    broadcast(notice_client_new, conn)
    prompt(conn, client_ip)
    
    try:
        while True:
            data = conn.recv(1024).decode().strip()
            
            if data == "":
                prompt(conn, client_ip)
                continue
            else:
                if not data:
                    break

                if data.lower() in ['/online', '/on']:
                    with clients_lock:
                        online_client = [f"- {c[1][0]}:{c[1][1]}" for c in clients]
                    msg = f"{CYAN}[*] Online Client:{RESET}\n{'\n'.join(online_client)}"
                    conn.sendall((msg + "\n").encode())
                    prompt(conn, client_ip)
                    continue
                
                if data.lower() in ['/exit', '/quit', '/ex', '/q']:
                    conn.sendall(f"{CYAN}[*] Disconnecting...{RESET}\n".encode())
                    break

            
            msg = f"\n{CYAN}{client_ip}: {RESET}{data}"
            smsg = f"{CYAN}[{get_time_now()}] {client_ip}: {RESET}{data}"
            print(smsg)
            broadcast(msg, conn)
            
            prompt(conn, client_ip)
            
    except Exception as ex:
        print(f"[{GRAY}{get_time_now()}] Error handling client ({client_ip}:{client_port}): {ex}{RESET}")
    finally:
        with clients_lock:
            clients[:] = [(c, a) for (c, a) in clients if c is not conn]

        notice_client_quit = f"\n{RED}[-] Client {client_ip}:{client_port} close connection{RESET}"
        snotice_client_quit = f"{RED}[{get_time_now()}] Client {client_ip}:{client_port} close connection{RESET}"
        print(snotice_client_quit)
        broadcast(notice_client_quit, client_ip)
        
def main():
    server_ip = get_ip_addr()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sck:
        sck.bind((HOST, PORT))
        sck.listen(5)
        print(f"{GRAY}[*] Server running in {HOST}:{PORT}{RESET}")
        print(f"{GRAY}[*] CLient join with 'nc {server_ip} {PORT}'{RESET}")
        print('='*50)
        try:
            while True:
                conn, addr = sck.accept()
                threading.Thread(target=client, args=(conn, addr), daemon=True).start()
                
        except KeyboardInterrupt:
            print('\n'+'='*50)
            print(f"{GRAY}[!] Server close the connection{RESET}")

if __name__ == '__main__':
    main()