
import http.server as hserver
import shutil
import pathlib


HTML_PATH = pathlib.Path.home() / "public_html"


class TalosServerHandler(hserver.BaseHTTPRequestHandler):

    def do_GET(self):
        file = self.get_file(self.path)

    def get_file(self, path):
        path = self.normalize_path(path)
        print(path / '.html')

        if pathlib.Path.is_file(path):
            print("Is a file")
            self.serve_file(path)
        elif pathlib.Path.is_dir(path):
            print("Is a dir")
            path = path / 'index.html'
            if path.is_file():
                self.serve_file(path)
        elif path.with_suffix(".html").is_file():
            print("Is a bare file")
            path = path.with_suffix(".html")
            self.serve_file(path)
        else:
            print("Doesn't exist")
            path = HTML_PATH / "404.html"
            self.serve_file(path)
        return path

    def normalize_path(self, path):
        if path == "/":
            path = "/index"
        path = HTML_PATH.joinpath(path.lstrip("/"))
        print(path)
        return pathlib.Path(path)

    def serve_file(self, path):
        with path.open("rb") as file:
            shutil.copyfileobj(file, self.wfile)


def main():
    server_address = ('', 80)
    server = hserver.HTTPServer(server_address, TalosServerHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
