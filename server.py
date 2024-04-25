import socket
import threading
from threading import Semaphore

MAX_CLIENTS = 2
MAX_MESSAGE_LEN = 256
client_sockets = {}
client_count = 0
client_lock = threading.Lock()
semaphore = Semaphore()

#each client is assigned their own thread to handle messages
def handle_client(client_socket, client_address):
    #client_count keeps track of each client with an ID
    global client_count

    with semaphore:
        client_id = client_count
        client_count += 1
    
    print(f"New client connected with ID: {client_id} from: {client_address}")
    username = client_socket.recv(MAX_MESSAGE_LEN).decode("utf-8").strip()
    print(f"Username for client ID {client_id} is {username}")
    client_sockets[client_id] = (username, client_socket)

    #listening for messages from client
    while True:
        try:
            message = client_socket.recv(MAX_MESSAGE_LEN).decode("utf-8")
            if not message:
                break
            print(f"Message from {username}: {message}")
            if message.startswith("exit "):
                exit_username = message.split(" ", 1)[1]
                if exit_username == username:
                    break
            broadcast_message(client_id, message)
        #if client disconnects, remove them from the list of connected clients
        except Exception as e:
            print(f"{username} disconnected.")
            del client_sockets[client_id]
            client_socket.close()
            break

#sends a client's message to all other connected clients, not including the sender
def broadcast_message(sender_id, message):
    with client_lock:
        for client_id, (username, client_socket) in client_sockets.items():
            if client_id != sender_id:
                try:
                    client_socket.send((f"Message from {username}: {message}").encode("utf-8"))
                except Exception as e:
                    continue

def main():
    #setup
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("127.0.0.1", 9734))
    server_socket.listen(5)
    print("Server waiting...")

    #create thread for any new clients
    while True:
        client_socket, client_address = server_socket.accept()
        if(client_count < MAX_CLIENTS):
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()
        else:
            client_socket.send(("Maximum clients connected to server. Please try again.").encode("utf-8"))
            client_socket.close()

if __name__ == "__main__":
    main()