
import http.server as hserver
import io
import shutil
import pathlib


HTML_PATH = pathlib.Path.home() / "public_html"

WEBMASTER_EMAIL = "talos.ptp@gmail.com"
BACKUP_ERROR = """
While attempting to handle HTTP code {0}, an unexpected error occured resulting in HTTP code {1}.

Error:
{2}

Please contact the webmaster at {3}.
"""
KNOWN_MIMES = {
    ".css": "text/css",
    ".html": "text/html",
    ".ico": "image/x-icon",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml"
}


class TalosServerHandler(hserver.BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.get_path(self.path)
        self.serve_file(path)

    def do_HEAD(self):
        path = self.get_path(self.path)
        self.serve_file(path, head=True)

    def do_POST(self):
        pass

    def get_path(self, path):
        # any hardcoded redirects here
        if path == "/":
            path = "/index"
        path = HTML_PATH.joinpath(path.lstrip("/"))
        return pathlib.Path(path)

    def serve_file(self, path, head=False):
        if pathlib.Path.is_file(path):
            self.send_file(path, head=head)
        elif pathlib.Path.is_dir(path):
            path = path / 'index.html'
            print(path.with_name(str(path.parent.name) + ".html"))
            if path.is_file():
                self.send_file(path, head=head)
                return path
            path = path.with_name(str(path.parent.name) + ".html")
            if path.is_file():
                self.send_file(path, head=head)
                return path
            else:
                self.error_code(404)
                return path
        elif path.with_suffix(".html").is_file():
            path = path.with_suffix(".html")
            self.send_file(path, head=head)
        else:
            self.error_code(404)
        return path

    def error_code(self, code):
        path = self.get_path(f"{code}.html")
        try:
            self.send_file(path, code=code)
        except Exception as e:
            self.backup_error_code(code, 404, e)

    def backup_error_code(self, old_code, new_code, error=None):
        self.send_response(new_code)
        self.end_headers()
        file = io.BytesIO(bytes(BACKUP_ERROR.format(old_code, new_code, error, WEBMASTER_EMAIL), "utf-8"))
        shutil.copyfileobj(file, self.wfile)

    def guess_mime(self, path):
        if KNOWN_MIMES.get(path.suffix):
            return KNOWN_MIMES[path.suffix]
        return "application/octet-stream"

    def send_file(self, path, *, code=200, mime_type=None, head=False):
        if mime_type is None:
            mime_type = self.guess_mime(path)
        with path.open("rb") as file:
            self.send_response(code)
            self.send_header("Content-Type", mime_type)
            self.end_headers()
            if not head:
                shutil.copyfileobj(file, self.wfile)


def main():
    server_address = ('', 80)
    server = hserver.HTTPServer(server_address, TalosServerHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
