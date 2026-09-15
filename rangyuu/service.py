import os,hmac,hashlib,json,logging,time,threading
from . import config
from http.server import BaseHTTPRequestHandler,HTTPServer
def handler_class(secret=""):
 log=logging.getLogger("rangyuu.http")
 lock=threading.Lock(); requests={}
 max_body=1_000_000; max_objective=2000
 class Handler(BaseHTTPRequestHandler):
  def _send(self,status,data):
   raw=json.dumps(data,separators=(",",":"),ensure_ascii=False).encode(); self.send_response(status); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
  def do_GET(self):
   if self.path=="/health": self._send(200,{"status":"ok"})
   else: self._send(404,{"error":"not found"})
  def do_POST(self):
   if self.path.split("?",1)[0]!="/orchestrate": self._send(404,{"error":"not found"}); return
   if not secret: self._send(503,{"error":"authentication not configured"}); return
   if self.headers.get("Content-Type","").split(";")[0].lower()!="application/json": self._send(415,{"error":"json required"}); return
   try: length=int(self.headers.get("Content-Length","-1"))
   except ValueError: self._send(400,{"error":"invalid content length"}); return
   if length<0: self._send(411,{"error":"content length required"}); return
   if self.headers.get("Transfer-Encoding"): self._send(411,{"error":"content length required"}); return
   if length>max_body: self._send(413,{"error":"payload too large"}); return
   body=self.rfile.read(length)
   if len(body)!=length: self._send(400,{"error":"truncated body"}); return
   sig=self.headers.get("X-Signature","")
   expected=hmac.new(secret.encode(),body,hashlib.sha256).hexdigest()
   if secret and not hmac.compare_digest(sig.removeprefix("sha256="),expected): self._send(401,{"error":"invalid signature"}); return
   try:
    payload=json.loads(body,parse_constant=lambda _: (_ for _ in ()).throw(ValueError("invalid number")))
    if not isinstance(payload,dict): self._send(400,{"error":"json object required"}); return
    objective=payload.get("objective")
    if not isinstance(objective,str) or not objective.strip() or len(objective)>max_objective:
     self._send(422,{"error":"objective must be a non-empty string of at most 2000 characters"}); return
    now=time.monotonic(); key=self.client_address[0]
    with lock:
     recent=[t for t in requests.get(key,[]) if now-t<60];
     if len(recent)>=30: self._send(429,{"error":"rate limit exceeded"}); return
     recent.append(now); requests[key]=recent
    log.info("request accepted path=%s bytes=%d",self.path,length); self._send(202,{"accepted":True,"objective":objective})
   except (json.JSONDecodeError,ValueError): self._send(400,{"error":"invalid json"})
  def log_message(self,*args): pass
 return Handler
def run():
 port=int(config.get("PORT","8080")); HTTPServer(("0.0.0.0",port),handler_class(config.get("RING_WEBHOOK_SECRET") or config.get("RANGYUU_WEBHOOK_SECRET",""))).serve_forever()
