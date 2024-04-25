import socket
import threading

MAX_CLIENTS = 100
MAX_MESSAGE_LEN = 256
client_sockets = {}
client_count = 0
client_lock = threading.Lock()

def handle_client(client_socket, client_address):
    global client_count
    client_id = client_count
    client_count += 1
    print("New client connected with ID:", client_id, "from:", client_address)
    username = client_socket.recv(MAX_MESSAGE_LEN).decode("utf-8").strip()
    print("Username for client ID", client_id, "is", username)
    client_sockets[client_id] = (username, client_socket)

    while True:
        try:
            message = client_socket.recv(MAX_MESSAGE_LEN).decode("utf-8")
            if not message:
                break
            print("Message from", username + ":", message)
            if message.startswith("exit "):
                exit_username = message.split(" ", 1)[1]
                if exit_username == username:
                    break
            broadcast_message(client_id, message)
        except Exception as e:
            print(username + " disconnected.")
            del client_sockets[client_id]
            client_socket.close()
            break

def broadcast_message(sender_id, message):
    with client_lock:
        for client_id, (username, client_socket) in client_sockets.items():
            if client_id != sender_id:
                try:
                    client_socket.send(("Message from " + username + ": " + message).encode("utf-8"))
                except Exception as e:
                    continue

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 9734))
    server_socket.listen(5)
    print("Server waiting...")

    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()