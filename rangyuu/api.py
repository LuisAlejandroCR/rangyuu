import json,hmac,hashlib
from http.server import BaseHTTPRequestHandler
from .ring import observation_from_event
from .policy import decision_report
class RingApiState:
 def __init__(self,secret): self.secret=secret; self.last=None
def make_handler(state):
 class H(BaseHTTPRequestHandler):
  def out(self,c,d): self.send_response(c); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps(d).encode())
  def do_GET(self):
   if self.path=='/api/rover/can-traverse': self.out(200, decision_report(device_id='unknown',timestamp='', **({} if not state.last else {'coverage':True,'session_active':True,'homography_valid':True,'free':True,'confidence':state.last.confidence,'unknown':False}))); return
   self.out(404,{'error':'not found'})
  def do_POST(self):
   if self.path!='/api/webhook/ring': self.out(404,{'error':'not found'}); return
   if not state.secret: self.out(503,{'error':'authentication unavailable'}); return
   try: n=int(self.headers.get('Content-Length','-1'))
   except ValueError: self.out(400,{'error':'invalid length'}); return
   if n<0 or n>1048576: self.out(400,{'error':'invalid body'}); return
   body=self.rfile.read(n); sig=self.headers.get('X-Signature',''); exp=hmac.new(state.secret.encode(),body,hashlib.sha256).hexdigest()
   if not hmac.compare_digest(sig.removeprefix('sha256='),exp): self.out(401,{'error':'invalid signature'}); return
   try: state.last=observation_from_event(json.loads(body))
   except (ValueError,TypeError,KeyError, json.JSONDecodeError): self.out(422,{'error':'invalid observation'}); return
   self.out(202,{'accepted':True})
  def log_message(self,*a): pass
 return H
