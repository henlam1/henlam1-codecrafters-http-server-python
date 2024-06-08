import socket
import threading
import argparse
import os

# Constants
CRLF = "\r\n"
ENCODINGS = set(["gzip"])

# Generate responses
def generate_response(status, content_type, body, encoding=None):
    response = [
        f"HTTP/1.1 {status}",  # Version and status
    ]
    # Encoding header
    if encoding:
        response.append(f"Content-Encoding: {encoding}")
    # GET requests
    if content_type or body:
        add_ons = [
            f"Content-Type: {content_type}",  # Headers
            f"Content-Length: {len(body)}",
            f"",  # End of headers
            body,
        ]
        response.extend(add_ons)
    # POST requests
    else:
        response.append(CRLF)
    return CRLF.join(response)

# Handle routes
def handle_root():
    return "HTTP/1.1 200 OK\r\n\r\n"

def handle_echo(request, path, version, headers, body):
    content = path.split("/echo/")[1]
    encodings = headers.get("accept-encoding").split(', ')  # split encodings into a list

    # Check each encoding
    for encoding in encodings:
        # Encoding found
        if encoding in ENCODINGS:  
            return generate_response("200 OK", "text/plain", content, encoding)

    # Encodings not found
    return generate_response("200 OK", "text/plain", content)
    
def handle_user_agent(request, path, version, headers, body):
    # Return 404 if not found
    agent = headers.get('user-agent')
    if agent is None:
        return handle_404()
    
    # Return user agent
    return generate_response("200 OK", "text/plain", agent)

def read_file(path):
    # Return 404 if not found
    if not os.path.isfile(path):
        return handle_404()
    
    # Return file content
    content = None
    with open(path, "r") as file:
        content = file.read()
    return generate_response("200 OK", "application/octet-stream", content)

def write_file(path, content):
    # Write to file
    with open(path, "w") as file:
        file.write(content)
    return generate_response("201 Created", "", "")

def handle_files(request, path, version, headers, body):
    # Create file path
    file_name = path.split("/files/")[1]
    path_to_file = f"{base_directory}/{file_name}"

    # Handle different requests
    if request == "GET":
        return read_file(path_to_file)
    if request == "POST":
        return write_file(path_to_file, body)
    
    return handle_404()
    

def handle_404():
    return "HTTP/1.1 404 Not Found\r\n\r\n"

def handle_endpoints(request, path, version, headers, body):
    # Handles root first
    if path == '/':
        return handle_root()
    
    # Split params by '/' delimeter
    params = path.split('/')

    # Handle all other endpoints
    endpoint = params[1]
    if endpoint in ROUTES:
        handler = ROUTES[endpoint]
        return handler(request, path, version, headers, body)
        
    # Return error if endpoint not found
    return handle_404()

# Routing Table
ROUTES = {
    'echo': handle_echo,
    'user-agent': handle_user_agent,
    'files': handle_files
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
        headers[header.lower()] = value # lower-case all headers for consistency
    body = lines[-1]
    
    return request, path, version, headers, body

def handle_request(client_socket: socket, addr):
    print(f"Connection to {addr} has been established")

    # Receive 1024 bytes from the client
    data = client_socket.recv(1024)

    # Parse request into usable components
    request, path, version, headers, body = parse_request(data)

    # Handle request
    response = handle_endpoints(request, path, version, headers, body)

    # Send the encoded response to the client
    client_socket.send(response.encode())

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Parse CLI arguments
    parser = argparse.ArgumentParser(
                    prog='main.py',
                    description='Simple HTTP server')
    parser.add_argument("--directory", type=str, help="Directory to change to.")
    args = parser.parse_args()

    # Set directory globally
    global base_directory
    base_directory = args.directory

    # Create server socket and connect to clients
    server_socket = socket.create_server(("localhost", 4221))
    server_socket.settimeout(0.1) # Set timeout 

    try:
        while True:
            try:
                # Wait for a connection
                client, addr = server_socket.accept() # wait for client

                # Create a new thread for each request
                thread = threading.Thread(target=handle_request, args=(client, addr))
                thread.start()
            # Timeout allows checks for KeyboardInterrupt
            except TimeoutError:    
                pass
    except KeyboardInterrupt:
        print("\nServer is shutting down.")
    finally:
        # Close server socket
        server_socket.close()
        print("Server shut down.")


if __name__ == "__main__":
    main()
