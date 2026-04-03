from http.server import HTTPServer, BaseHTTPRequestHandler
import os

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def log_message(self, format, *args):
        # suppress log messages
        pass

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health check server running on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
