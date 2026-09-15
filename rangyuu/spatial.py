from dataclasses import dataclass
from .geometry import project_point
from .policy import decision_report,cell_is_stale
@dataclass(frozen=True)
class CellObservation: cell:tuple; observed_at:float; confidence:float; free:bool; source:str
class SpatialState:
 def __init__(self,max_age=30): self.max_age=max_age; self.calibrations={}; self.cells={}; self.events=set()
 def calibrate(self,device_id,h): self.calibrations[device_id]=h
 def ingest(self,event):
  eid=event.get('event_id') or event.get('id');
  if eid in self.events:return False
  if eid:self.events.add(eid)
  d=event['device_id']; h=self.calibrations.get(d)
  if h is None: return False
  b=event['bounding_box']; x=(b[0]+b[2])/2; y=b[3]; p=project_point(h,(x,y)); cell=(round(p[0]),round(p[1]))
  self.cells[cell]=CellObservation(cell,float(event['timestamp']),float(event['confidence']),bool(event.get('free',False)),event.get('source','ring')); return True
 def evaluate_trajectory(self,device_id,timestamp,trajectory):
  if not trajectory:return decision_report(device_id=device_id,timestamp=timestamp,coverage=False)
  vals=[self.cells.get(tuple(c)) for c in trajectory]; stale=any(v is None or cell_is_stale(v.observed_at,float(timestamp),self.max_age) for v in vals)
  unknown=any(v is None for v in vals); occupied=any(v and not v.free for v in vals); conf=min((v.confidence for v in vals if v),default=0)
  return decision_report(device_id=device_id,timestamp=timestamp,cells=trajectory,coverage=not unknown,session_active=True,homography_valid=device_id in self.calibrations,free=not occupied,confidence=conf,unknown=unknown,stale=stale)
