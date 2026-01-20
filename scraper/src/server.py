"""
Job Crawler - Scraper Server

A lightweight HTTP server to listen for crawl triggers from the web UI.
"""

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from datetime import datetime

from .main import run_crawler

# Global lock to prevent concurrent crawls
CRAWL_LOCK = threading.Lock()

class CrawlerRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/crawl':
            if CRAWL_LOCK.locked():
                self.send_response(409)  # Conflict
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'message': 'Crawl already in progress'
                }).encode())
                return

            # Start crawl in a separate thread to not block the response
            thread = threading.Thread(target=self.run_background_crawl)
            thread.start()

            self.send_response(202)  # Accepted
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'accepted',
                'message': 'Crawl started'
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def run_background_crawl(self):
        """Run the crawler safely with a lock."""
        with CRAWL_LOCK:
            print(f"[{datetime.now()}] Triggered crawl starting...")
            try:
                # Reload config/DB connection if needed inside run_crawler
                # We save to DB and print verbose output
                run_crawler(save_to_db=True, verbose=True)
                print(f"[{datetime.now()}] Triggered crawl finished successfully.")
            except Exception as e:
                print(f"[{datetime.now()}] Triggered crawl failed: {e}", file=sys.stderr)

    def do_GET(self):
        # Health check
        if self.path == '/health':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CrawlerRequestHandler)
    print(f"Scraper server listening on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
