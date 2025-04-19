from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 设置响应状态码
        self.send_response(200)
        # 设置响应头
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        # 返回响应内容
        self.wfile.write(b'Hello, World!')

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler, port=8888):
    server_address = ('', port)  # 监听所有地址
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
