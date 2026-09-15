import hashlib,hmac,json
from dataclasses import dataclass
@dataclass(frozen=True)
class Observation:
    device_id:str; timestamp:str; kind:str; confidence:float; bbox:tuple|None
def verify_hmac(body, signature, secret):
    expected=hmac.new(secret.encode(), body if isinstance(body,bytes) else body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.removeprefix("sha256="))
def observation_from_event(event):
    data=event.get("data",event); box=data.get("bounding_box")
    bbox=tuple(box) if isinstance(box,(list,tuple)) else (tuple(box.values()) if isinstance(box,dict) else None)
    return Observation(str(event.get("device_id",data.get("device_id","unknown"))),str(event.get("timestamp",data.get("timestamp",""))),str(event.get("type",data.get("type","unknown"))),float(data.get("confidence",0)),bbox)
