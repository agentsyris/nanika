from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nanika AI System</title>
            <style>
                body { font-family: Arial; padding: 50px; background: #0a0a0a; color: #fff; }
                h1 { color: #00ff88; }
            </style>
        </head>
        <body>
            <h1>Nanika System</h1>
            <p>AI Chat Backend - Operational</p>
            <p>View source: <a href="https://github.com/agentsyris/nanika">GitHub Repository</a></p>
        </body>
        </html>
        ''')
