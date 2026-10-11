"""Dev-only stand-in for API Gateway, so you can test AWS mode without Docker or an AWS account.

It wraps the REAL Lambda handler in a tiny HTTP server (POST /calculate). It is not
part of the AWS deployment. Run:  python scripts/local_api.py   (listens on :3000)
Then:  RAINWISE_API_URL=http://127.0.0.1:3000/calculate streamlit run app.py
"""
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from rainwise.handler import lambda_handler  # noqa: E402


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/calculate":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", errors="replace")
        res = lambda_handler({"body": body, "isBase64Encoded": False})
        payload = res["body"].encode()
        self.send_response(res["statusCode"])
        for k, v in res["headers"].items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        sys.stderr.write("[local-api] " + fmt % args + "\n")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    print(f"Local RainWise API on http://127.0.0.1:{port}/calculate")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
