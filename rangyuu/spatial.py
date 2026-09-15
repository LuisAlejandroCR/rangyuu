from dataclasses import dataclass
import math
from .geometry import project_point
from .policy import decision_report,cell_is_stale
@dataclass(frozen=True)
class CellObservation: cell:tuple; observed_at:float; confidence:float; free:bool; source:str
class SpatialState:
 def __init__(self,max_age=30,cell_size=1): self.max_age=max_age; self.cell_size=cell_size; self.calibrations={}; self.cells={}; self.events=set()
 def calibrate(self,device_id,h):
  if len(h)!=3 or any(len(r)!=3 or not all(math.isfinite(float(x)) for x in r) for r in h): raise ValueError('invalid calibration')
  self.calibrations[device_id]=h
 def ingest(self,event):
  eid=event.get('event_id') or event.get('id');
  d=event['device_id']; h=self.calibrations.get(d)
  if h is None: return False
  b=event['bounding_box']; ts=float(event['timestamp']); conf=float(event['confidence'])
  if len(b)!=4 or not all(math.isfinite(float(x)) for x in b) or b[2]<0 or b[3]<0 or not 0<=conf<=1: raise ValueError('invalid event')
  if eid in self.events:return False
  if eid:self.events.add(eid)
  x=b[0]+b[2]/2; y=b[1]+b[3]; p=project_point(h,(x,y)); cell=(math.floor(p[0]/self.cell_size),math.floor(p[1]/self.cell_size))
  free=event.get('kind') in ('clear','motion_clear'); source=event.get('source','ring')
  if source not in ('ring','iphone'): raise ValueError('invalid source')
  old=self.cells.get(cell)
  if old is None or ts>=old.observed_at:self.cells[cell]=CellObservation(cell,ts,conf,free,source)
  return True
 def evaluate_trajectory(self,device_id,timestamp,trajectory):
  if not trajectory:return decision_report(device_id=device_id,timestamp=timestamp,coverage=False)
  vals=[self.cells.get(tuple(c)) for c in trajectory]; stale=any(v is None or cell_is_stale(v.observed_at,float(timestamp),self.max_age) for v in vals)
  unknown=any(v is None for v in vals); occupied=any(v and not v.free for v in vals); conf=min((v.confidence for v in vals if v),default=0)
  return decision_report(device_id=device_id,timestamp=timestamp,cells=trajectory,coverage=not unknown,session_active=True,homography_valid=device_id in self.calibrations,free=not occupied,confidence=conf,unknown=unknown,stale=stale)
