import socket

def handle_request(client_socket: socket):
    # Receive 1024 bytes from the client
    client_socket.recv(1024)

    # Send the encoded response to the client
    response = "HTTP/1.1 200 OK\r\n\r\n"
    client_socket.send(response.encode())

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Create server socket and connect to clients
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client, addr = server_socket.accept() # wait for client
    
    # Handle request and close connection
    handle_request(client)
    client.close()


if __name__ == "__main__":
    main()
