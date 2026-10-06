"""원자료 병합 -> data/dataset.csv (Misery Index, 주식·채권 총수익지수 계산)."""
import pandas as pd, numpy as np
S='./raw/'   # clone한 원자료 폴더 경로 (README 참조)
F=S+'macro_eco_dashboard/public/data/fred/'
def fred(n):
    d=pd.read_csv(F+n+'.csv',parse_dates=['observation_date']).set_index('observation_date')[n]
    return pd.to_numeric(d,errors='coerce')
U=fred('UNRATE'); FF=fred('FEDFUNDS'); CPI=fred('CPIAUCSL'); REC=fred('USREC')
dgs=fred('DGS10').resample('MS').mean()
y10=pd.read_csv(S+'bond-yields-us-10y/data/monthly.csv',parse_dates=['Date']).set_index('Date')['Rate']
sp=pd.read_csv(S+'s-and-p-500/data/data.csv',parse_dates=['Date']).set_index('Date')
gold=pd.read_csv(S+'gold-prices/data/monthly-processed.csv',parse_dates=['Date']).set_index('Date')['Price']
hp=pd.read_csv(S+'house-prices-us/data/national-month.csv',parse_dates=['Date']).set_index('Date')['National-US-SA']
df=pd.DataFrame({'U':U,'FF':FF,'CPI':CPI,'REC':REC,'Y10':y10.combine_first(dgs)})
df['SP']=sp['SP500']; df['DIV']=sp['Dividend'].replace(0,np.nan).ffill()
df['GOLD']=gold; df['HPI']=hp
df=df.loc['1953-04':'2026-08']
# spot checks
print(df.loc[['1982-11-01','1981-01-01','2009-10-01','2020-04-01'],['U','FF','Y10']])
df['INF']=df.CPI.pct_change(12)*100
df['MISERY']=df.U+df.INF
# equity total return index (monthly avg price + div/12)
r=df.SP.pct_change()+df.DIV.shift(1)/12/df.SP.shift(1)
df['EQ_TR']=(1+r.fillna(0)).cumprod()
# 10y constant maturity bond TR: buy par at y_{t-1}, reprice at y_t with 119 months left
y0=df.Y10.shift(1)/100; y1=df.Y10/100
n=120; m=y0/2
def price(c,y,periods):
    # semiannual coupon c (annual), yield y, periods in half-years
    return c/2*(1-(1+y/2)**(-periods))/(y/2)+(1+y/2)**(-periods)
br=price(y0,y1,(n-1)/6)-1+y0/12
df['BOND_TR']=(1+br.fillna(0)).cumprod()
df.to_csv('data/dataset.csv')
print(df.tail(3)); print(df.describe().T[['count','min','max']])
