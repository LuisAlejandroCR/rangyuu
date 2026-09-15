import os,hmac,hashlib,json
from http.server import BaseHTTPRequestHandler,HTTPServer
def handler_class(secret=""):
 class Handler(BaseHTTPRequestHandler):
  def _send(self,status,data):
   raw=json.dumps(data).encode(); self.send_response(status); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(raw)
  def do_GET(self):
   if self.path=="/health": self._send(200,{"status":"ok"})
   else: self._send(404,{"error":"not found"})
  def do_POST(self):
   if self.path!="/orchestrate": self._send(404,{"error":"not found"}); return
   length=int(self.headers.get("Content-Length","0"));
   if length>1_000_000: self._send(413,{"error":"payload too large"}); return
   body=self.rfile.read(length); sig=self.headers.get("X-Signature","")
   expected=hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
   if secret and not hmac.compare_digest(sig.removeprefix("sha256="),expected): self._send(401,{"error":"invalid signature"}); return
   try: payload=json.loads(body); self._send(200,{"accepted":True,"objective":payload.get("objective","")[:2000]})
   except json.JSONDecodeError: self._send(400,{"error":"invalid json"})
  def log_message(self,*args): pass
 return Handler
def run():
 port=int(os.getenv("PORT","8080")); HTTPServer(("0.0.0.0",port),handler_class(os.getenv("RANGYUU_WEBHOOK_SECRET",""))).serve_forever()
