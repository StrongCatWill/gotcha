"""Gotcha backend — zero-dependency stdlib server.

Run:  python3 backend/server.py   then open  http://localhost:8000

Serves the frontend (index.html) and a small JSON API:
  GET  /api/jobs?skills=React,Python&types=Remote,Graduate
  POST /api/events/swipe        {"role":..,"dir":"right","skills":[...]}
  GET  /api/insights/top-skill
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

import jobs  # same directory

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root (holds index.html)


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/api/jobs":
            qs = parse_qs(u.query)
            skills = [s for s in (qs.get("skills", [""])[0]).split(",") if s]
            types = [t for t in (qs.get("types", [""])[0]).split(",") if t]
            return self._json({"jobs": jobs.get_jobs(skills, types)})
        if u.path == "/api/insights/top-skill":
            return self._json({"skill": jobs.top_skill()})
        # static: index.html + anything else in repo root
        return self._static(u.path)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/api/cv":
            n = int(self.headers.get("Content-Length") or 0)
            try:
                payload = json.loads(self.rfile.read(n) or b"{}")
            except Exception:
                payload = {}
            skills = jobs.detect_skills(payload.get("text", ""))
            return self._json({"skills": skills})
        if u.path == "/api/events/swipe":
            n = int(self.headers.get("Content-Length") or 0)
            try:
                payload = json.loads(self.rfile.read(n) or b"{}")
            except Exception:
                payload = {}
            jobs.EVENTS.append(payload)
            return self._json({"ok": True, "total": len(jobs.EVENTS),
                               "top_skill": jobs.top_skill()})
        return self._json({"error": "not found"}, 404)

    def _static(self, path):
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        fp = os.path.normpath(os.path.join(ROOT, rel))
        if not fp.startswith(ROOT) or not os.path.isfile(fp):
            return self._json({"error": "not found"}, 404)
        ctype = "text/html" if fp.endswith(".html") else "application/octet-stream"
        with open(fp, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):  # quieter console
        pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"Gotcha running →  http://localhost:{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
