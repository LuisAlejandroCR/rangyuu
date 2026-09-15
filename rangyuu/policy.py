from dataclasses import dataclass
from enum import Enum
class Decision(str,Enum): PROCEED="PROCEED"; HOLD="HOLD"; UNKNOWN="UNKNOWN"
def cell_is_stale(observed_at, now, max_age):
    if not isinstance(now,(int,float)) or not isinstance(max_age,(int,float)) or max_age<0: raise ValueError("invalid age")
    if observed_at is None: return True
    if not isinstance(observed_at,(int,float)) or observed_at<0: raise ValueError("invalid timestamp")
    return now-observed_at >= max_age
def decision_report(*,device_id,timestamp,cells=(),**kwargs):
    if kwargs.get('contradiction'): reason='contradiction'
    elif not kwargs.get('coverage',True): reason='camera offline/session unavailable'
    elif kwargs.get('homography_valid',True) is False: reason='homography invalid/derived'
    elif kwargs.get('unknown'): reason='trajectory unknown'
    elif kwargs.get('stale'): reason='cell stale'
    elif kwargs.get('confidence',1)<.5: reason='low confidence'
    else: reason='clear high-confidence path'
    allowed={k:v for k,v in kwargs.items() if k in ('coverage','confidence','free','unknown','stale','contradiction')}
    if kwargs.get('homography_valid') is False: allowed['coverage']=False
    d=Decision.UNKNOWN if reason=='low confidence' else decide(**allowed)
    return {"decision":d.value,"action":"WAIT" if d!=Decision.PROCEED else "TRAVERSE","reason":reason,"evidence":{"device_id":device_id,"timestamp":timestamp,"cells":list(cells)}}
def decide(*,coverage=True,confidence=1.0,free=True,unknown=False,stale=False,contradiction=False):
    if not coverage or unknown or stale or contradiction: return Decision.HOLD
    if confidence < .5: return Decision.UNKNOWN
    return Decision.PROCEED if free else Decision.HOLD
