import socket
from routing import *

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
