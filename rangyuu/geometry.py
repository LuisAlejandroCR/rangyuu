"""Small, dependency-free planar calibration utilities."""
from math import hypot
def _normalize(points):
    cx=sum(x for x,y in points)/len(points); cy=sum(y for x,y in points)/len(points)
    d=sum(hypot(x-cx,y-cy) for x,y in points)/len(points)
    s=2**.5/d if d>1e-12 else 1
    return [((x-cx)*s,(y-cy)*s) for x,y in points], ((s,0,-s*cx),(0,s,-s*cy),(0,0,1))
def _mm(a,b): return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

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
    ns,ts=_normalize(src); nd,td=_normalize(dst)
    a=[]; b=[]
    for (x,y),(u,v) in zip(ns,nd):
        a += [[x,y,1,0,0,0,-u*x,-u*y],[0,0,0,x,y,1,-v*x,-v*y]]
        b += [u,v]
    if len(a)>8:
        ata=[[sum(row[i]*row[j] for row in a) for j in range(8)] for i in range(8)]
        atb=[sum(row[i]*z for row,z in zip(a,b)) for i in range(8)]
        h=_solve(ata,atb)
    else: h=_solve(a,b)
    H=[h[:3],h[3:6],[h[6],h[7],1.0]]
    s=ts[0][0]; tx=ts[0][2]; ty=ts[1][2]; q=td[0][0]; ux=td[0][2]; uy=td[1][2]
    inv=((1/q,0,-ux/q),(0,1/q,-uy/q),(0,0,1))
    out=_mm(inv,_mm(H,ts)); z=out[2][2]
    return [[v/z for v in row] for row in out]

def project_point(h, p):
    x,y=p; q=h[2][0]*x+h[2][1]*y+h[2][2]
    if abs(q)<1e-12: raise ValueError("point projects to infinity")
    return ((h[0][0]*x+h[0][1]*y+h[0][2])/q,(h[1][0]*x+h[1][1]*y+h[1][2])/q)
