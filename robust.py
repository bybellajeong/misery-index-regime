"""강건성 검증: 임계값 스윕, 10Y 금리 기준 레짐, 비중첩 연간, 실질수익률 등."""
from analysis import *
print("== threshold sweep EQ corr (low side cU,cI | high side cU,cI)")
for k in [1,2,3,4,5,6,7,8]:
    lo=df[df.FF0<k]; hi=df[df.FF0>=k]
    f=lambda s,v: round(s.R_EQ.corr(s[v]),2)
    print(k,len(lo),f(lo,'dU'),f(lo,'dINF'),'|',len(hi),f(hi,'dU'),f(hi,'dINF'))
print("== regime by 10Y yield (<4 / >=6)")
df['Y0']=df.Y10.shift(12)
for lo,hi in [(0,4),(4,6),(6,99)]:
    s=df[(df.Y0>=lo)&(df.Y0<hi)]
    print(lo,hi,len(s),[ (a,round(s['R_'+a].corr(s.dU),2),round(s['R_'+a].corr(s.dINF),2)) for a in assets])
print("== non-overlapping Dec-Dec annual, FF<3 vs >=5")
a=df[df.index.month==12]
for lo,hi in [(0,3),(3,6),(6,99)]:
    s=a[(a.FF0>=lo)&(a.FF0<hi)]
    print(lo,hi,len(s),round(s.R_EQ.corr(s.dU),2),round(s.R_EQ.corr(s.dINF),2))
print("== real equity returns")
df['R_EQR']=df.R_EQ-np.log(df.CPI).diff(12)*100
for lo,hi in [(0,3),(3,6),(6,99)]:
    s=df[(df.FF0>=lo)&(df.FF0<hi)]; print(lo,hi,round(s.R_EQR.corr(s.dU),2),round(s.R_EQR.corr(s.dINF),2))
print("== misery delta alone vs components (R2)")
for lo,hi in [(0,3),(3,6),(6,99)]:
    s=df[(df.FF0>=lo)&(df.FF0<hi)].dropna(subset=['R_EQ','dMIS'])
    print(lo,hi,'mis corr',round(s.R_EQ.corr(s.dMIS),2))
print("== forward 12m equity returns vs trailing dU,dINF")
df['F_EQ']=df.R_EQ.shift(-12); df['FF_now']=df.FF
for lo,hi in [(0,3),(3,6),(6,99)]:
    s=df[(df.FF>=lo)&(df.FF<hi)].dropna(subset=['F_EQ'])
    print(lo,hi,len(s),round(s.F_EQ.corr(s.dU),2),round(s.F_EQ.corr(s.dINF),2), 'level', round(s.F_EQ.corr(s.U),2), round(s.F_EQ.corr(s.INF),2))
print("== monthly stock-bond corr by regime")
m=pd.read_csv('data/dataset.csv',index_col=0,parse_dates=True)
m['e']=m.EQ_TR.pct_change(); m['b']=m.BOND_TR.pct_change(); m['FF0']=m.FF.shift(1)
for lo,hi in [(0,3),(3,6),(6,99)]:
    s=m[(m.FF0>=lo)&(m.FF0<hi)]; print(lo,hi,round(s.e.corr(s.b),2))
print("== periods")
P={'1965-1982':('1965','1982'),'1983-2007':('1983','2007'),'2009-2021':('2009','2021'),'2022-2026':('2022','2026')}
for n,(a_,b_) in P.items():
    s=df.loc[a_:b_]; print(n, round(s.FF.mean(),1), [ (a,round(s['R_'+a].corr(s.dU),2),round(s['R_'+a].corr(s.dINF),2)) for a in assets])
