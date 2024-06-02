import socket

def handle_request(client_socket: socket):
    # Constants
    CRLF = "\r\n"

    # Receive 1024 bytes from the client
    data = client_socket.recv(1024)

    # Decode and split data
    request, header, *body = data.decode().split(CRLF)

    # Parse request
    url = request.split(" ")[1]
    if url != '/':
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    else:
        response = "HTTP/1.1 200 OK\r\n\r\n"

    # Send the encoded response to the client
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
