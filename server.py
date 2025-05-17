import socket
import threading

HOST =  socket.gethostbyname(socket.gethostname()) # Her yerden bağlanabilir
PORT = 5059
print(HOST , PORT)
clients = []

def handle_client(conn, addr):
    print(f"Connected: {addr}")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            # Diğer clientlara ilet
            for c in clients:
                if c != conn:
                    c.sendall(data)
        except:
            break
    print(f"Disconnected: {addr}")
    clients.remove(conn)
    conn.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print("server açıldı")
    while True:
        conn, addr = server.accept()
        clients.append(conn)
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
   main()