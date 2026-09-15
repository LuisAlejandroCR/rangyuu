"""Small, dependency-free planar calibration utilities."""
from math import hypot

def _solve(a, b):
    n=len(b); m=[list(map(float,a[i]))+[float(b[i])] for i in range(n)]
    for c in range(n):
        p=max(range(c,n), key=lambda i: abs(m[i][c]))
        if abs(m[p][c]) < 1e-12: raise ValueError("degenerate correspondences")
        m[c],m[p]=m[p],m[c]
        q=m[c][c]; m[c]=[x/q for x in m[c]]
        for i in range(n):
            if i!=c:
                q=m[i][c]; m[i]=[x-q*y for x,y in zip(m[i],m[c])]
    return [m[i][-1] for i in range(n)]

def homography_dlt(src, dst):
    if len(src)<4 or len(src)!=len(dst): raise ValueError("need four matching points")
    # Fix h33 only when numerically safe; this is the 8-parameter DLT solution.
    a=[]; b=[]
    for (x,y),(u,v) in zip(src,dst):
        a += [[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]
        b += [u,v]
    h=_solve(a,b); return [h[:3],h[3:6],[h[6],h[7],1.0]]

def project_point(h, p):
    x,y=p; q=h[2][0]*x+h[2][1]*y+h[2][2]
    if abs(q)<1e-12: raise ValueError("point projects to infinity")
    return ((h[0][0]*x+h[0][1]*y+h[0][2])/q,(h[1][0]*x+h[1][1]*y+h[1][2])/q)
