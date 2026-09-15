import hashlib,hmac,json,math
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
    device=event.get("device_id",data.get("device_id")); stamp=event.get("timestamp",data.get("timestamp")); kind=event.get("type",data.get("type")); conf=data.get("confidence")
    if not device or not stamp or not kind or conf is None or not 0<=float(conf)<=1: raise ValueError('invalid observation')
    if bbox is not None and (len(bbox)!=4 or not all(math.isfinite(float(x)) for x in bbox)): raise ValueError('invalid bbox')
    return Observation(str(device),str(stamp),str(kind),float(conf),bbox)
