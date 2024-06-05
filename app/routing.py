from response import *

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
    endpoint = params[1]
    if endpoint in ROUTES:
        handler = ROUTES[endpoint]
        return handler(request, path, version, headers)
        
    # Return error if endpoint not found
    return handle_404()

# Routing Table
ROUTES = {
    'echo': handle_echo,
    'user-agent': handle_user_agent,
}