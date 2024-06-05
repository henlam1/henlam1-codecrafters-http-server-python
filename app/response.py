from constants import *

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