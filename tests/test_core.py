import hashlib,hmac
from rangyuu import *
from rangyuu.policy import cell_is_stale, decision_report
def test_homography():
 h=homography_dlt([(0,0),(1,0),(1,1),(0,1)],[(2,3),(4,3),(4,5),(2,5)])
 assert all(abs(a-b)<1e-9 for a,b in zip(project_point(h,(.5,.5)),(3.0,4.0)))
def test_degenerate_rejected():
 try: homography_dlt([(0,0),(1,0),(2,0),(3,0)],[(0,0),(1,0),(2,0),(3,0)])
 except ValueError: return
 raise AssertionError('degenerate points must be rejected')
def test_hmac_and_event():
 body=b'{"type":"motion_detected"}'; sig=hmac.new(b"s",body,hashlib.sha256).hexdigest()
 assert verify_hmac(body,sig,"s") and not verify_hmac(body,sig[:-1]+"0","s")
 o=observation_from_event({"device_id":"d","timestamp":"t","type":"person","data":{"confidence":.8,"bounding_box":[1,2,3,4]}})
 assert o.device_id=="d" and o.bbox==(1,2,3,4)
def test_degradation_rows():
 assert decide()==Decision.HOLD
 assert decide(coverage=True,session_active=True,homography_valid=True,
               confidence=1,free=True,unknown=False)==Decision.PROCEED
 assert decide(unknown=True)==Decision.HOLD
 assert decide(coverage=False)==Decision.HOLD
 assert decide(coverage=True,session_active=True,homography_valid=True,
               confidence=.2,free=True,unknown=False)==Decision.UNKNOWN
 assert decide(contradiction=True)==Decision.HOLD
def test_initial_state_and_expiry():
 assert cell_is_stale(None,100,30) and cell_is_stale(50,100,30)
 assert not cell_is_stale(80,100,30)
def test_decision_evidence_and_unknown_never_authorizes():
 r=decision_report(device_id='d',timestamp='t',cells=[1],unknown=True,free=True,confidence=1)
 assert r['decision']=='HOLD' and r['evidence']['device_id']=='d'
 assert decision_report(device_id='d',timestamp='t',coverage=False)['decision']=='HOLD'
 ok=decision_report(device_id='d',timestamp='t',coverage=True,session_active=True,
                    homography_valid=True,confidence=1,free=True,unknown=False)
 assert ok['decision']=='PROCEED' and ok['action']=='TRAVERSE'
def test_homography_reason_and_boundary():
 assert decision_report(device_id='d',timestamp='t',homography_valid=False)['decision']=='HOLD'
 assert decision_report(device_id='d',timestamp='t',contradiction=True,free=True,confidence=1)['reason']=='contradiction'
 assert cell_is_stale(70,100,30) and not cell_is_stale(71,100,30)
