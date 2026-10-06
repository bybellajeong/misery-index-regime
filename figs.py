"""보고서 그림 1-7 생성 및 결과표(data/results.json) 저장."""
import os; os.makedirs("figures",exist_ok=True)
import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import json
for f in fm.findSystemFonts():
    if 'CJK' in f: fm.fontManager.addfont(f)
plt.rcParams.update({'font.family':'Noto Sans CJK JP','font.size':9,'axes.spines.top':False,'axes.spines.right':False,
 'axes.edgecolor':'#8a8984','axes.labelcolor':'#52514e','xtick.color':'#52514e','ytick.color':'#52514e',
 'axes.grid':True,'grid.color':'#e6e5e0','grid.linewidth':0.6,'axes.axisbelow':True,'figure.facecolor':'white',
 'axes.titlesize':10,'axes.titleweight':'bold','axes.titlelocation':'left','legend.frameon':False,'axes.unicode_minus':False})
BLUE,ORANGE,AQUA,YELLOW,VIOLET='#2a78d6','#eb6834','#1baf7a','#eda100','#4a3aa7'
INK2='#52514e'; GRAY='#b9b8b2'
from analysis import *
REG=[(0,3,'저금리 (FF<3%)'),(3,6,'중금리 (3–6%)'),(6,99,'고금리 (FF≥6%)')]
AN={'EQ':'주식 (S&P500 TR)','BOND':'미국채 10Y TR','HOME':'주택 (Case-Shiller)','GOLD':'금'}
out={}
def save(fig,n): fig.savefig(f'figures/fig{n}.png',dpi=220,bbox_inches='tight'); plt.close(fig)

# Fig1 misery history + FF
full=pd.read_csv('data/dataset.csv',index_col=0,parse_dates=True).loc['1955':]
fig,(a1,a2)=plt.subplots(2,1,figsize=(7.2,4.6),sharex=True,gridspec_kw={'height_ratios':[2.2,1]})
for s,e in [(s,e) for s,e in zip(full.index,full.index[1:])][:0]: pass
rec=full.REC.fillna(0)
for ax in (a1,a2):
    ax.fill_between(full.index,0,1,where=rec>0,transform=ax.get_xaxis_transform(),color='#ecebe6',lw=0)
a1.plot(full.index,full.MISERY,color='#0b0b0b',lw=1.4,label='Misery Index')
a1.plot(full.index,full.U,color=BLUE,lw=1.1,label='실업률')
a1.plot(full.index,full.INF,color=ORANGE,lw=1.1,label='CPI 인플레이션(YoY)')
a1.set_ylabel('%'); a1.legend(ncol=3,loc='upper right',fontsize=8)
a1.set_title('그림 1. 미국 Misery Index와 구성요소 (1955–2026, 음영=NBER 경기침체)')
a2.plot(full.index,full.FF,color=VIOLET,lw=1.1)
a2.axhline(3,color=GRAY,ls='--',lw=0.8); a2.axhline(6,color=GRAY,ls='--',lw=0.8)
a2.text(full.index[5],6.4,'6%',color=INK2,fontsize=7); a2.text(full.index[5],3.4,'3%',color=INK2,fontsize=7)
a2.set_ylabel('연방기금금리 %'); save(fig,1)

# Fig2 rolling 10y corr (equities)
w=120
rc_u=df.R_EQ.rolling(w).corr(df.dU); rc_i=df.R_EQ.rolling(w).corr(df.dINF); ffm=df.FF.rolling(w).mean()
fig,(a1,a2)=plt.subplots(2,1,figsize=(7.2,4.4),sharex=True,gridspec_kw={'height_ratios':[2,1]})
a1.plot(rc_u.index,rc_u,color=BLUE,lw=1.4,label='주식수익률 × Δ실업률')
a1.plot(rc_i.index,rc_i,color=ORANGE,lw=1.4,label='주식수익률 × Δ인플레이션')
a1.axhline(0,color='#8a8984',lw=0.8); a1.set_ylim(-1,1); a1.legend(loc='upper left',ncol=2,fontsize=8)
a1.set_ylabel('상관계수'); a1.set_title('그림 2. 10년 rolling 상관계수: 주식 12개월 수익률 vs 실업률·인플레이션 12개월 변화')
a2.plot(ffm.index,ffm,color=VIOLET,lw=1.2); a2.set_ylabel('FF 10년 평균 %'); save(fig,2)

# Fig3 threshold sweep
ks=np.arange(1,9.01,0.5); rows=[]
for k in ks:
    lo=df[df.FF0<k]; hi=df[df.FF0>=k]
    rows.append([lo.R_EQ.corr(lo.dU),lo.R_EQ.corr(lo.dINF),hi.R_EQ.corr(hi.dU),hi.R_EQ.corr(hi.dINF)])
rows=np.array(rows)
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.2,2.8),sharey=True)
for ax,j,t in [(a1,0,'임계값 아래 구간 (저금리 측)'),(a2,2,'임계값 이상 구간 (고금리 측)')]:
    ax.plot(ks,rows[:,j],color=BLUE,lw=1.6,marker='o',ms=3.5,label='Δ실업률')
    ax.plot(ks,rows[:,j+1],color=ORANGE,lw=1.6,marker='o',ms=3.5,label='Δ인플레이션')
    ax.axhline(0,color='#8a8984',lw=0.8); ax.set_title(t,fontsize=9); ax.set_xlabel('연방기금금리 임계값 (%)')
a1.set_ylabel('주식수익률과의 상관계수'); a1.legend(fontsize=8,loc='lower left')
fig.suptitle('그림 3. 금리 임계값을 바꿔도 결론이 유지되는가 (주식)',x=0.02,ha='left',fontsize=10,fontweight='bold',y=1.03)
save(fig,3)

# Fig4 heatmap all assets
from matplotlib.colors import LinearSegmentedColormap
cmap=LinearSegmentedColormap.from_list('div',['#e34948','#f0efec','#2a78d6'])
M=[];res={}
for a in assets:
    rowv=[]
    for lo,hi,_ in REG:
        s=df[(df.FF0>=lo)&(df.FF0<hi)]
        r=run(s,a); res[(a,lo)]=r; rowv+= [r['cU'],r['cI']]
    M.append(rowv)
M=np.array(M)
fig,ax=plt.subplots(figsize=(7.2,2.9))
ax.imshow(M,cmap=cmap,vmin=-0.8,vmax=0.8,aspect='auto'); ax.grid(False)
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_xticks(range(6)); ax.set_xticklabels(['Δ실업률','Δ인플레'] *3)
ax.set_yticks(range(4)); ax.set_yticklabels([AN[a] for a in assets])
for i in range(4):
    for j in range(6):
        ax.text(j,i,f'{M[i,j]:+.2f}',ha='center',va='center',fontsize=9,color='#0b0b0b',fontweight='bold' if abs(M[i,j])>=0.3 else 'normal')
for j,(lo,hi,n) in enumerate(REG): ax.text(2*j+0.5,-0.7,n,ha='center',fontsize=9,fontweight='bold',color='#0b0b0b')
for x in [1.5,3.5]: ax.axvline(x,color='white',lw=4)
ax.tick_params(length=0); ax.set_title('그림 4. 금리 레짐별 자산 12개월 수익률과 거시변수 변화의 상관계수',pad=30)
save(fig,4)

# Fig5 misery alone vs components (equities)
fig,ax=plt.subplots(figsize=(7.2,2.7)); x=np.arange(3); wd=0.26
vals=[[],[],[]]
for lo,hi,_ in REG:
    s=df[(df.FF0>=lo)&(df.FF0<hi)]
    vals[0].append(s.R_EQ.corr(s.dMIS)); vals[1].append(s.R_EQ.corr(s.dU)); vals[2].append(s.R_EQ.corr(s.dINF))
for k,(v,c,l) in enumerate(zip(vals,['#0b0b0b',BLUE,ORANGE],['ΔMisery Index','Δ실업률','Δ인플레이션'])):
    b=ax.bar(x+(k-1)*wd,v,wd*0.9,color=c,label=l)
    for xi,vi in zip(x+(k-1)*wd,v): ax.text(xi,vi+(0.03 if vi>=0 else -0.03),f'{vi:+.2f}',ha='center',va='bottom' if vi>=0 else 'top',fontsize=7.5,color='#0b0b0b')
ax.axhline(0,color='#8a8984',lw=0.8); ax.set_xticks(x); ax.set_xticklabels([r[2] for r in REG]); ax.set_ylim(-0.65,0.4)
ax.set_ylabel('주식수익률과의 상관'); ax.legend(ncol=3,fontsize=8,loc='lower left')
ax.set_title('그림 5. 동일가중 Misery Index는 저금리 구간에서 설명력을 잃는다'); save(fig,5)
out['misery']=vals

# Fig6 scatter small multiples
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.2,3.0))
lo=df[df.FF0<3].dropna(subset=['R_EQ','dU']); hi=df[df.FF0>=6].dropna(subset=['R_EQ','dINF'])
for ax,s,v,c,t,xl in [(a1,lo,'dU',BLUE,'저금리: 주식 vs Δ실업률','Δ실업률 (%p, 12M)'),(a2,hi,'dINF',ORANGE,'고금리: 주식 vs Δ인플레이션','Δ인플레이션 (%p, 12M)')]:
    ax.scatter(s[v],s.R_EQ,s=9,color=c,alpha=0.45,lw=0)
    bb=np.polyfit(s[v],s.R_EQ,1); xx=np.linspace(s[v].min(),s[v].max(),10); ax.plot(xx,np.polyval(bb,xx),color='#0b0b0b',lw=1.3)
    ax.set_title(f'{t}  (ρ={s.R_EQ.corr(s[v]):+.2f})',fontsize=9); ax.set_xlabel(xl); ax.axhline(0,color='#8a8984',lw=0.6)
a1.set_ylabel('S&P500 12개월 로그수익률 (%)')
fig.suptitle('그림 6. 레짐별 핵심 변수와 주식수익률의 산포도 (월별, 중첩 12개월)',x=0.02,ha='left',fontsize=10,fontweight='bold',y=1.03); save(fig,6)

# Fig7 stock-bond corr
m=pd.read_csv('data/dataset.csv',index_col=0,parse_dates=True)
m['e']=m.EQ_TR.pct_change(); m['b']=m.BOND_TR.pct_change(); m['FF0']=m.FF.shift(1)
sb=[ (lambda s: s.e.corr(s.b))(m[(m.FF0>=lo)&(m.FF0<hi)]) for lo,hi,_ in REG]
fig,ax=plt.subplots(figsize=(4.6,2.3))
bars=ax.bar(range(3),sb,0.5,color=[BLUE,'#b9b8b2',ORANGE])
for i,v in enumerate(sb): ax.text(i,v+(0.01 if v>=0 else -0.01),f'{v:+.2f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=8)
ax.axhline(0,color='#8a8984',lw=0.8); ax.set_xticks(range(3)); ax.set_xticklabels([r[2] for r in REG],fontsize=8); ax.set_ylim(-0.35,0.4)
ax.set_title('그림 7. 레짐별 주식–채권 월간수익률 상관',fontsize=9.5); save(fig,7)
out['sb']=sb

# tables
tab={}
for a in assets:
    for lo,hi,n in REG: tab[f'{a}|{n}']={k:float(v) for k,v in res[(a,lo)].items()}
out['tab']=tab
json.dump(out,open('data/results.json','w'),ensure_ascii=False,indent=1,default=float)
print(json.dumps(out['misery'],default=float), out['sb'])
