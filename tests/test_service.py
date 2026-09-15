import json,threading,urllib.request,urllib.error
from http.server import HTTPServer
from rangyuu.service import handler_class
def test_http_contract():
 s=HTTPServer(('127.0.0.1',0),handler_class('secret')); threading.Thread(target=s.serve_forever,daemon=True).start(); u='http://127.0.0.1:%d'%s.server_port
 r=urllib.request.urlopen(u+'/health'); assert r.status==200
 req=urllib.request.Request(u+'/orchestrate',b'{}',headers={'Content-Type':'application/json','X-Signature':'bad'})
 try: urllib.request.urlopen(req)
 except urllib.error.HTTPError as e: assert e.code==401
 s.shutdown()
