from dataclasses import dataclass
from enum import Enum
class Decision(str,Enum): PROCEED="PROCEED"; HOLD="HOLD"; UNKNOWN="UNKNOWN"
def decide(*,coverage=True,confidence=1.0,free=True,unknown=False,stale=False,contradiction=False):
    if not coverage or unknown or stale or contradiction: return Decision.HOLD
    if confidence < .5: return Decision.UNKNOWN
    return Decision.PROCEED if free else Decision.HOLD
