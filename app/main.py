import socket
import threading
import argparse
import os
import gzip

# Constants
CRLF = "\r\n"

# # Generate responses
# def generate_response(status, content_type, body, encoding=None):
#     headers = [
#         f"HTTP/1.1 {status}",  # Version and status
#     ]
#     # Encoding header
#     if encoding:
#         headers.append(f"Content-Encoding: {encoding}")
#         # Compress body to assigned encoding
#         compressor = ENCODINGS[encoding]
#         body = compressor(body.encode)
#     # Convert body to bytes for consistency
#     if body:
#         if isinstance(body, str):
#             body = body.encode()
#     # GET requests
#     if content_type:
#         headers.extend([
#             f"Content-Type: {content_type}",  # Headers
#             f"Content-Length: {len(body)}",
#             f"",  # End of headers
#         ])
    
#     # Convert headers to bytes
#     header_bytes = CRLF.join(headers).encode()

#     # Return body with headers
#     if body:
#         return header_bytes + CRLF.encode() + body
    
#     return header_bytes

# Generate responses
def generate_response(status, content_type, body, encoding=None):
    response = [
        f"HTTP/1.1 {status}",  # Version and status
    ]
    # Encoding header
    if encoding:
        response.append(f"Content-Encoding: {encoding}")

    # GET requests
    if content_type and body:
        # Add extra headers
        add_ons = [
            f"Content-Type: {content_type}",  # Headers
            f"Content-Length: {len(body)}",
            f"",  # End of headers
        ]
        response.extend(add_ons)

        # Convert body into bytes for consistency (sometimes bytes or string)
        if isinstance(body, str):
            body = body.encode()
    # POST requests
    else:
        response.append(CRLF)

    # Convert response into bytes
    response = CRLF.join(response).encode()

    if body:
        response = response + CRLF.encode() + body
    
    return response


# Handle encodings
def gzip_compress(content):
    return gzip.compress(content)

# Encoding table
ENCODINGS = {
    'gzip': gzip_compress
}

# Handle routes
def handle_root():
    # return "HTTP/1.1 200 OK\r\n\r\n".encode()
    return generate_response("200 OK", "", "")

def handle_echo(request, path, version, headers, body):
    content = path.split("/echo/")[1]
    encodings = headers.get("accept-encoding")  # Either encodings or None

    # No encodings
    if encodings is None:
        return generate_response("200 OK", "text/plain", content)

    # Check each encoding
    encodings = encodings.split(", ")   # split encodings into a list
    for encoding in encodings:
        # Encoding found
        if encoding in ENCODINGS:
            compressor = ENCODINGS[encoding]
            content = compressor(content.encode())
            return generate_response("200 OK", "text/plain", content, encoding)

    # Encodings are invalid
    return generate_response("200 OK", "text/plain", content)
    
def handle_user_agent(request, path, version, headers, body):
    # Return 404 if not found
    agent = headers.get('user-agent')
    if agent is None:
        return handle_404()
    
    # Return user agent
    return generate_response("200 OK", "text/plain", agent)

def handle_404():
    # return "HTTP/1.1 404 Not Found\r\n\r\n".encode()
    return generate_response("404 Not Found", "", "")

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

# File read/writes
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

# Routing Table
ROUTES = {
    'echo': handle_echo,
    'user-agent': handle_user_agent,
    'files': handle_files
}

# Handle requests
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
    client_socket.send(response)

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
