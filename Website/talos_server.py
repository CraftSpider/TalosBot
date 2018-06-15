
import http.server as hserver


class TalosServerHandler(hserver.BaseHTTPRequestHandler):

    def do_GET(self):
        print(self.path)


def main():
    server_address = ('', 80)
    server = hserver.HTTPServer(server_address, handler_class=TalosServerHandler)
    server.serve_forever()
