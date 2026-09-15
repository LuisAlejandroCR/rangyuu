from dataclasses import dataclass
from enum import Enum
class Decision(str,Enum): PROCEED="PROCEED"; HOLD="HOLD"; UNKNOWN="UNKNOWN"
def cell_is_stale(observed_at, now, max_age):
    return observed_at is None or now-observed_at > max_age
def decide(*,coverage=True,confidence=1.0,free=True,unknown=False,stale=False,contradiction=False):
    if not coverage or unknown or stale or contradiction: return Decision.HOLD
    if confidence < .5: return Decision.UNKNOWN
    return Decision.PROCEED if free else Decision.HOLD
