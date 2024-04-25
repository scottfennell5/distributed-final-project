import socket
import threading

MAX_MESSAGE_LEN = 256

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(MAX_MESSAGE_LEN).decode("utf-8")
            if not message:
                print("Error recieving message.")
                sock.close()
                exit(1)
            print(message)
        except Exception as e:
            print("Server disconnected.")
            sock.close()
            exit(1)

def main():
    sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockfd.connect(("127.0.0.1", 9734))

    username = input("Enter a username: ")
    sockfd.send(username.encode("utf-8"))

    #start thread to recieve messages
    receive_thread = threading.Thread(target=receive_messages, args=(sockfd,))
    receive_thread.start()

    print(f"Type any character and hit 'Enter' to send. Send 'exit {username}' to exit.")
    #for sending messages
    while True:
        message = input()
        if message.startswith("exit "):
            exit_username = message.split(" ", 1)[1]
            if exit_username == username:
                sockfd.send(message.encode("utf-8"))
                sockfd.close()
                exit()
        sockfd.send(message.encode("utf-8"))

if __name__ == "__main__":
    main()