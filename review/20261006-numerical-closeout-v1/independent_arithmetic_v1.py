# 独立算术复核：不调用R检验函数，不重新拟合。
from pathlib import Path
import json
import numpy as np
import csv
def read(p):
    with p.open() as f:return list(csv.DictReader(f))
o=Path(__file__).resolve().parent
a=read(o/'search_audit/RW_ALL_240.csv')
x=np.loadtxt(o/'search_audit/BOOTSTRAP_TEST_VALUES.csv',delimiter=',',skiprows=1)
assert x.shape==(200,240)
pt=np.array([float(r['point_test_scale']) for r in a]);sd=x.std(axis=0,ddof=1)
obs=np.abs(pt/sd);boot=np.abs((x-pt)/sd)
def rw(ids):
    order=np.array(ids)[np.argsort(-obs[ids],kind='stable')]
    out=np.zeros(len(a));previous=0
    for j,i in enumerate(order):
        p=(1+np.sum(boot[:,order[j:]].max(axis=1)>=obs[i]))/(len(x)+1)
        previous=max(previous,p);out[i]=previous
    return out
np.testing.assert_allclose(sd,[float(r['se_bootstrap']) for r in a],rtol=1e-10)
np.testing.assert_allclose(rw(np.arange(len(a))),[float(r['p_RW_all240']) for r in a],atol=1e-12)
for metric in ['TNIE','Delta_CDE']:
    ids=np.array([i for i,r in enumerate(a) if r['metric']==metric])
    np.testing.assert_allclose(rw(ids)[ids],[float(a[i]['p_RW_within_metric']) for i in ids],atol=1e-12)
d=read(o/'exports/P3_ALL_6000_DRAWS.csv')
points={r['component']:r for r in read(o/'exports/P3_POINTS.csv')}
tests={r['component']:r for r in read(o/'exports/P3_OMNIBUS.csv')}
checks=[]
for tag in ['original','capped']:
    mat=np.array([[float(r[k]) for k in ['d_5vle3','d_5v4']] for r in d if r['component']==tag])
    p=np.array([float(points[tag][k]) for k in ['d_5vle3','d_5v4']])
    v=np.cov(mat,rowvar=False);iv=np.linalg.inv(v)
    t0=p@iv@p;center=mat-p
    tt=np.einsum('ij,jk,ik->i',center,iv,center)
    tail=int(np.sum(tt>=t0));prob=(1+tail)/2001
    assert tail==int(tests[tag]['tail_count'])
    assert abs(prob-float(tests[tag]['p_raw']))<1e-12
    checks.append(dict(component=tag,tail_count=tail,p_raw=prob,statistic=float(t0)))
fam=read(o/'exports/SIX_TEST_FAMILY.csv');ps=np.array([float(r['p_raw']) for r in fam])
order=np.argsort(ps);m=len(ps)
adj=np.minimum.accumulate((ps[order]*m/np.arange(1,m+1))[::-1])[::-1]
bh=np.empty(m);bh[order]=np.minimum(1,adj);by=np.minimum(1,bh*np.sum(1/np.arange(1,m+1)))
np.testing.assert_allclose(bh,[float(r['q_BH6']) for r in fam],atol=1e-12)
np.testing.assert_allclose(by,[float(r['q_BY6']) for r in fam],atol=1e-12)
result=dict(status='PASS',search_tests=240,search_draws=200,p3=checks,six_family_verified=True,scope='Independent arithmetic, not independent model refit or calibration proof')
(o/'exports/INDEPENDENT_ARITHMETIC.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
