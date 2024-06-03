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
    response = handle_endpoints(url)

    # Send the encoded response to the client
    client_socket.send(response.encode())

def handle_endpoints(url: str):
    # Handles / path
    if url == '/':
        return "HTTP/1.1 200 OK\r\n\r\n"
    
    # Handles other paths
    elif url.startswith('/echo/'):
        path = url.split("/echo/")
        content = path[1]
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(content)}\r\n\r\n{content}"
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"

    return response

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
