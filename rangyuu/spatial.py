"""Validated in-memory spatial occupancy state."""
from dataclasses import dataclass
import math
import numpy as np
from .geometry import project_point
from .policy import cell_is_stale, decision_report

FREE_KINDS={"clear","motion_clear","path_clear"}; OCCUPIED_KINDS={"motion_detected","object","person","vehicle"}; SOURCES={"ring","iphone"}
@dataclass(frozen=True)
class CellObservation:
    cell:tuple[int,int]; observed_at:float; confidence:float; free:bool; source:str; device_id:str

def _number(value,name):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(float(value)): raise ValueError(f"{name} must be finite numeric")
    return float(value)

class SpatialState:
 def __init__(self,max_age=30,cell_size=1):
  self.max_age=_number(max_age,"max_age"); self.cell_size=_number(cell_size,"cell_size")
  if self.max_age<=0 or self.cell_size<=0: raise ValueError("spatial limits must be positive")
  self.calibrations={}; self.cells={}; self.events=set(); self.contradictions=set()
 def calibrate(self,device_id,h):
  matrix=np.asarray(h,dtype=float)
  if not isinstance(device_id,str) or not device_id.strip() or matrix.shape!=(3,3) or not np.isfinite(matrix).all() or abs(float(np.linalg.det(matrix)))<=np.finfo(float).eps*np.linalg.norm(matrix)**3: raise ValueError("invalid calibration")
  self.calibrations[device_id]=matrix.tolist()
 def ingest(self,event):
  if not isinstance(event,dict): raise ValueError("event must be an object")
  eid=event.get("event_id") or event.get("id"); device=event.get("device_id"); kind=event.get("kind") or event.get("type"); source=event.get("source","ring")
  if not isinstance(eid,str) or not eid.strip() or not isinstance(device,str) or not device.strip(): raise ValueError("event and device ids are required")
  if kind not in FREE_KINDS|OCCUPIED_KINDS or source not in SOURCES: raise ValueError("unsupported observation")
  timestamp=_number(event.get("timestamp"),"timestamp"); confidence=_number(event.get("confidence"),"confidence")
  if timestamp<0 or not 0<=confidence<=1: raise ValueError("invalid timestamp or confidence")
  bbox=event.get("bounding_box")
  if not isinstance(bbox,(list,tuple)) or len(bbox)!=4: raise ValueError("bounding_box must be [x,y,width,height]")
  x,y,width,height=(_number(v,"bounding_box") for v in bbox)
  if width<0 or height<0: raise ValueError("bounding_box dimensions cannot be negative")
  if eid in self.events:return False
  homography=self.calibrations.get(device)
  if homography is None:return False
  world=project_point(homography,(x+width/2,y+height)); cell=(math.floor(world[0]/self.cell_size),math.floor(world[1]/self.cell_size)); key=(device,cell); free=kind in FREE_KINDS; previous=self.cells.get(key)
  if previous and timestamp==previous.observed_at and free!=previous.free:self.contradictions.add(key)
  elif previous is None or timestamp>previous.observed_at:self.contradictions.discard(key)
  if previous is None or timestamp>=previous.observed_at:self.cells[key]=CellObservation(cell,timestamp,confidence,free,source,device)
  self.events.add(eid); return True
 def evaluate_trajectory(self,device_id,timestamp,trajectory):
  now=_number(timestamp,"timestamp")
  if now<0 or not isinstance(device_id,str) or not device_id.strip(): raise ValueError("invalid evaluation context")
  if trajectory is None:trajectory=[]
  if not isinstance(trajectory,(list,tuple)) or len(trajectory)>64: raise ValueError("invalid trajectory")
  cells=[]
  for cell in trajectory:
   if not isinstance(cell,(list,tuple)) or len(cell)!=2 or any(isinstance(v,bool) or not isinstance(v,int) for v in cell): raise ValueError("cells must be integer pairs")
   cells.append(tuple(cell))
  if not cells:return decision_report(device_id=device_id,timestamp=now,coverage=False)
  values=[self.cells.get((device_id,cell)) for cell in cells]; unknown=any(v is None for v in values); stale=any(v is not None and cell_is_stale(v.observed_at,now,self.max_age) for v in values); occupied=any(v is not None and not v.free for v in values); confidence=min((v.confidence for v in values if v),default=0)
  return decision_report(device_id=device_id,timestamp=now,cells=cells,coverage=bool(device_id in self.calibrations),session_active=True,homography_valid=device_id in self.calibrations,free=not occupied,confidence=confidence,unknown=unknown,stale=stale,contradiction=any((device_id,c) in self.contradictions for c in cells))
