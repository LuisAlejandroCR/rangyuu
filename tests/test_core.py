import hashlib,hmac
from rangyuu import *
def test_homography():
 h=homography_dlt([(0,0),(1,0),(1,1),(0,1)],[(2,3),(4,3),(4,5),(2,5)])
 assert project_point(h,(.5,.5))==(3.0,4.0)
def test_hmac_and_event():
 body=b'{"type":"motion_detected"}'; sig=hmac.new(b"s",body,hashlib.sha256).hexdigest()
 assert verify_hmac(body,sig,"s") and not verify_hmac(body,sig[:-1]+"0","s")
 o=observation_from_event({"device_id":"d","timestamp":"t","type":"person","data":{"confidence":.8,"bounding_box":[1,2,3,4]}})
 assert o.device_id=="d" and o.bbox==(1,2,3,4)
def test_degradation_rows():
 assert decide()==Decision.PROCEED
 assert decide(unknown=True)==Decision.HOLD
 assert decide(coverage=False)==Decision.HOLD
 assert decide(confidence=.2)==Decision.UNKNOWN
 assert decide(contradiction=True)==Decision.HOLD
