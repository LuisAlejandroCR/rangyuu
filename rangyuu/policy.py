from dataclasses import dataclass
from enum import Enum
class Decision(str,Enum): PROCEED="PROCEED"; HOLD="HOLD"; UNKNOWN="UNKNOWN"
def cell_is_stale(observed_at, now, max_age):
    if not isinstance(now,(int,float)) or not isinstance(max_age,(int,float)) or max_age<0: raise ValueError("invalid age")
    if observed_at is None: return True
    if not isinstance(observed_at,(int,float)) or observed_at<0: raise ValueError("invalid timestamp")
    return now-observed_at >= max_age
def decision_report(*,device_id,timestamp,cells=(),coverage=False,session_active=False,
                    homography_valid=False,confidence=None,free=False,unknown=True,
                    stale=False,contradiction=False):
    if contradiction: reason='contradiction'
    elif not coverage: reason='camera offline'
    elif not session_active: reason='session unavailable'
    elif not homography_valid: reason='homography invalid/derived'
    elif unknown: reason='trajectory unknown'
    elif stale: reason='cell stale'
    elif confidence is None: reason='confidence missing'
    elif confidence < .5: reason='low confidence'
    elif not free: reason='path occupied'
    else: reason='clear high-confidence path'
    d=decide(coverage=coverage,session_active=session_active,
             homography_valid=homography_valid,confidence=confidence,free=free,
             unknown=unknown,stale=stale,contradiction=contradiction)
    return {"decision":d.value,"action":"WAIT" if d!=Decision.PROCEED else "TRAVERSE","reason":reason,"evidence":{"device_id":device_id,"timestamp":timestamp,"cells":list(cells)}}
def decide(*,coverage=False,session_active=False,homography_valid=False,confidence=None,free=False,unknown=True,stale=False,contradiction=False):
    if not coverage or not session_active or not homography_valid or unknown or stale or contradiction or not free: return Decision.HOLD
    if confidence is None or confidence < .5: return Decision.UNKNOWN
    return Decision.PROCEED if free else Decision.HOLD
