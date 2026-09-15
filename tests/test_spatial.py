from rangyuu.spatial import SpatialState
def test_spatial_lifecycle():
 s=SpatialState(10); h=[[1,0,0],[0,1,0],[0,0,1]]; s.calibrate('d',h)
 e={'event_id':'1','device_id':'d','timestamp':100,'bounding_box':[0,0,1,1],'confidence':.9,'free':True}; assert s.ingest(e); assert not s.ingest(e)
 assert s.evaluate_trajectory('d',100,[(0,1)])['decision']=='PROCEED'
 e['event_id']='2'; e['free']=False; s.ingest(e); assert s.evaluate_trajectory('d',100,[(0,1)])['decision']=='HOLD'
 assert s.evaluate_trajectory('d',100,[(9,9)])['decision']=='HOLD'
 assert s.evaluate_trajectory('x',100,[(0,1)])['decision']=='HOLD'
