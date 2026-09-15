"""Provider-agnostic planning contract; never logs credentials or sends unbounded payloads."""
from dataclasses import dataclass
import os, urllib.request, json, ipaddress
from urllib.parse import urlparse
@dataclass(frozen=True)
class Plan:
    objective:str; files:tuple[str,...]; max_tokens:int=4000
class ProviderAdapter:
    def plan(self, objective, files=()): raise NotImplementedError
    def generate_patch(self, plan): raise NotImplementedError
    def review(self, patch): raise NotImplementedError
class HttpProvider(ProviderAdapter):
    def __init__(self, base_url=None, token=None, max_bytes=1_000_000):
        self.base_url=(base_url or os.getenv("RANGYUU_PROVIDER_URL","" )).rstrip("/")
        self.token=token or os.getenv("RANGYUU_PROVIDER_TOKEN")
        self.max_bytes=max_bytes
        self._validate_url()
    def _validate_url(self):
        if not self.base_url: return
        u=urlparse(self.base_url)
        if u.scheme != "https": raise ValueError("provider URL must use HTTPS")
        try:
            ip=ipaddress.ip_address(u.hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local: raise ValueError("private provider address")
        except ValueError as e:
            if str(e)=="private provider address": raise
    def plan(self, objective, files=()):
        if not objective or len(objective)>2000: raise ValueError("objective exceeds limit")
        return Plan(objective,tuple(files),4000)
    def _post(self,path,payload):
        raw=json.dumps(payload).encode()
        if len(raw)>self.max_bytes: raise ValueError("payload exceeds limit")
        req=urllib.request.Request(self.base_url+path,raw,headers={"Content-Type":"application/json",**({"Authorization":"Bearer "+self.token} if self.token else {})})
        opener=urllib.request.build_opener(urllib.request.HTTPRedirectHandler())
        with opener.open(req,timeout=20) as r: return json.loads(r.read(self.max_bytes+1))
    def generate_patch(self, plan): return self._post("/generate",{"objective":plan.objective,"files":plan.files,"max_tokens":plan.max_tokens})
    def review(self, patch):
        if len(str(patch).encode())>self.max_bytes: raise ValueError("patch exceeds limit")
        return self._post("/review",{"patch":patch})
