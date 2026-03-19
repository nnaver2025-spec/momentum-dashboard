import http.server
import socketserver
import requests
import os
import sys

PORT = 8000

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for the proxy
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        # Proxy requests starting with /api/proxy/
        # Example: http://localhost:8000/api/proxy/index/KOSPI/basic
        # -> https://m.stock.naver.com/api/index/KOSPI/basic
        if self.path.startswith('/api/proxy/'):
            target_path = self.path[len('/api/proxy/'):]
            target_url = f"https://m.stock.naver.com/api/{target_path}"
            
            # Use headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://m.stock.naver.com/'
            }
            
            try:
                # print(f"Proxying request to: {target_url}")
                response = requests.get(target_url, headers=headers, timeout=5)
                
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    # Skip hop-by-hop headers
                    if key.lower() not in ['content-encoding', 'transfer-encoding', 'content-length', 'connection']:
                        self.send_header(key, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.content)
            except Exception as e:
                print(f"Proxy error: {e}")
                self.send_error(500, str(e))
        else:
            # Fallback to standard file server
            return super().do_GET()

if __name__ == "__main__":
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Allow port reuse to avoid "Address already in use" errors
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"===========================================")
        print(f"  Momentum Dashboard Server Started")
        print(f"  URL: http://localhost:{PORT}")
        print(f"  Real-time Proxy: Enabled")
        print(f"===========================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            httpd.shutdown()
            sys.exit(0)
