#!/usr/bin/env python3
"""
Markdown 文档查看器服务器
运行在 9063 端口
"""

import http.server
import socketserver
import os
import json
from urllib.parse import urlparse, parse_qs
import mimetypes

PORT = 9063
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MDHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/files':
            # 返回所有MD文件列表
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            files = [f for f in os.listdir(DIRECTORY) if f.endswith('.md')]
            files.sort()
            self.wfile.write(json.dumps(files).encode())

        elif parsed_path.path == '/api/content':
            # 返回指定文件的内容
            query = parse_qs(parsed_path.query)
            filename = query.get('file', [''])[0]

            if filename and filename.endswith('.md'):
                filepath = os.path.join(DIRECTORY, filename)
                if os.path.exists(filepath) and os.path.isfile(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({'content': content}).encode())
                    except Exception as e:
                        self.send_error(500, str(e))
                else:
                    self.send_error(404, 'File not found')
            else:
                self.send_error(400, 'Invalid file')

        elif parsed_path.path == '/' or parsed_path.path == '':
            self.path = '/index.html'
            super().do_GET()

        else:
            super().do_GET()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    with socketserver.TCPServer(("", PORT), MDHandler) as httpd:
        print(f"文档服务器运行在 http://localhost:{PORT}")
        print(f"文档目录: {DIRECTORY}")
        print("按 Ctrl+C 停止服务器")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已停止")


if __name__ == "__main__":
    main()
