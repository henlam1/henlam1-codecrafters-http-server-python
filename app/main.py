import socket

# Handle routes
def handle_root():
    return "HTTP/1.1 200 OK\r\n\r\n"

def handle_echo(path):
    content = path.split("/echo")[1]
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n{content}"

def handle_404():
    return "HTTP/1.1 404 Not Found\r\n\r\n"

# Routing Table
ROUTES = {
    '/echo': handle_echo,
    '/': handle_root,
}

def handle_request(client_socket: socket):
    # Constants
    CRLF = "\r\n"

    # Receive 1024 bytes from the client
    data = client_socket.recv(1024)

    # Decode and split data
    request, header, *body = data.decode().split(CRLF)

    # Parse request
    url = request.split(" ")[1]
    response = handle_endpoints(url)

    # Send the encoded response to the client
    client_socket.send(response.encode())

def handle_endpoints(url: str):
    for path, handler in ROUTES.items():
        if url.startswith(path):
            return handler(url)

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Create server socket and connect to clients
    server_socket = socket.create_server(("localhost", 4221))

    try:
        while True:
            # Wait for a connection
            client, addr = server_socket.accept() # wait for client
            print(f"Connection with {addr} established.")

            # Handle request and close connection
            handle_request(client)
            client.close()
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        # Close server socket
        server_socket.close()
        print("Server shut down.")


if __name__ == "__main__":
    main()
