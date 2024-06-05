import socket

# Constants
CRLF = "\r\n"

# Generate responses
def generate_response(status, content_type, body):
    response = [
        f"HTTP/1.1 {status}",   # Version and status
        f"Content-Type: {content_type}",    # Headers
        f"Content-Length: {len(body)}",
        f"",    # End of headers
        body
    ]
    return CRLF.join(response)

# Handle routes
def handle_root():
    return "HTTP/1.1 200 OK\r\n\r\n"

def handle_echo(request, path, version, headers):
    content = path.split("/echo/")[1]
    return generate_response("200 OK", "text/plain", content)

def handle_user_agent(request, path, version, headers):
    if 'User-Agent' not in headers:
        return handle_404()
    agent = headers['User-Agent']
    return generate_response("200 OK", "text/plain", agent)

def handle_404():
    return "HTTP/1.1 404 Not Found\r\n\r\n"

def handle_endpoints(request, path, version, headers):
    # Handles root first
    if path == '/':
        return handle_root()
    
    # Split params by '/' delimeter
    params = path.split('/')

    # Handle all other endpoints
    # for endpoint, handler in ROUTES.items():
    #     if path.startswith(endpoint):
    #         return handler(request, path, version, headers
    endpoint = params[1]
    if endpoint in ROUTES:
        handler = ROUTES[endpoint]
        return handler(request, path, version, headers)
        
    # Return error if endpoint not found
    return handle_404()

# Routing Table
ROUTES = {
    '/echo': handle_echo,
    '/user-agent': handle_user_agent,
}

def parse_request(data):
    # Decode and split data (requst, path, version, and headers)
    lines = data.decode().split(CRLF)
    start_line = lines[0]
    request, path, version = start_line.split(" ")
    headers = {}
    for line in lines[1:]:
        # Skip empty lines
        if not line: break

        # Build headers by separating colons
        header, value = line.split(": ", 1)
        headers[header] = value
    
    return request, path, version, headers

def handle_request(client_socket: socket):
    # Receive 1024 bytes from the client
    data = client_socket.recv(1024)

    # Parse request into usable components
    request, path, version, headers = parse_request(data)

    # Handle request
    response = handle_endpoints(request, path, version, headers)

    # Send the encoded response to the client
    client_socket.send(response.encode())

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
