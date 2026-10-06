"""금리 레짐별 회귀분석: 자산 12개월 수익률 ~ Δ실업률 + Δ인플레이션 (Newey-West 표준오차)."""
import pandas as pd, numpy as np
df=pd.read_csv('data/dataset.csv',index_col=0,parse_dates=True)
assets={'EQ':'EQ_TR','BOND':'BOND_TR','HOME':'HPI','GOLD':'GOLD'}
for k,c in assets.items(): df['R_'+k]=np.log(df[c]).diff(12)*100
df['dU']=df.U.diff(12); df['dINF']=df.INF.diff(12); df['dMIS']=df.MISERY.diff(12)
df['FF0']=df.FF.shift(12)  # regime at start of window
df=df.loc['1955-07':]
def nw_ols(y,X,L=12):
    X=np.column_stack([np.ones(len(X)),X]); b=np.linalg.lstsq(X,y,rcond=None)[0]; e=y-X@b
    XtXi=np.linalg.inv(X.T@X); S=np.zeros((X.shape[1],)*2)
    for l in range(L+1):
        w=1 if l==0 else 1-l/(L+1); G=(X[l:]*e[l:,None]).T@(X[:len(X)-l]*e[:len(X)-l,None])
        S+= w*(G if l==0 else G+G.T)
    V=XtXi@S@XtXi; r2=1-e.var()/y.var()
    return b,b/np.sqrt(np.diag(V)),r2
def run(sub,a):
    d=sub[['R_'+a,'dU','dINF']].dropna()
    if a=='GOLD': d=d.loc['1973':]
    if a=='HOME': d=d.loc['1988':]
    if len(d)<36: return None
    z=(d-d.mean())/d.std()
    b,t,r2=nw_ols(z['R_'+a].values,z[['dU','dINF']].values)
    return dict(n=len(d),cU=d['R_'+a].corr(d.dU),cI=d['R_'+a].corr(d.dINF),bU=b[1],tU=t[1],bI=b[2],tI=t[2],r2=r2)

if __name__=='__main__':
    for lo,hi in [(0,3),(3,6),(6,99),(0,4),(4,99)]:
        sub=df[(df.FF0>=lo)&(df.FF0<hi)]
        print(f'--- FF {lo}-{hi}: months {len(sub)}')
        for a in assets:
            r=run(sub,a)
            if r: print(a, {k:round(v,2) for k,v in r.items()})
