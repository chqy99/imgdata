import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(__file__), 'cmdlog')
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

class CmdHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length)
        try:
            entry = json.loads(data.decode())
            entry['timestamp'] = datetime.now().isoformat()
            with open(LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'ok')
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(e).encode())

def run_server(port=8765):
    server = HTTPServer(('127.0.0.1', port), CmdHandler)
    print(f'Service running on http://127.0.0.1:{port}')
    server.serve_forever()

if __name__ == '__main__':
    run_server()
