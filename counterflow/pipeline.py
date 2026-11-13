"""Walk-forward one-day demand prediction on synthetic operational data."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

FEATURES=['site_id','day_of_week','month','is_weekend','lag_1','lag_7','rolling_7','rolling_28']

def make_demo_data(days:int=220, sites:int=4,seed:int=42)->pd.DataFrame:
    if days<60 or sites<1: raise ValueError('need >=60 days and >=1 site')
    rng=np.random.default_rng(seed)
    start=pd.Timestamp('2025-01-01')
    records=[]
    for site in range(sites):
        for i in range(days):
            dt=start+pd.Timedelta(days=i)
            weekly=21 if dt.dayofweek in (4,5) else (-9 if dt.dayofweek==0 else 0)
            seasonal=7*np.sin(2*np.pi*i/28)
            demand=max(0,int(round(65+site*12+weekly+seasonal+rng.normal(0,7))))
            records.append((dt,site,demand))
    return pd.DataFrame(records,columns=['date','site_id','units']).sort_values(['site_id','date']).reset_index(drop=True)

def features(data:pd.DataFrame)->pd.DataFrame:
    required={'date','site_id','units'}
    if not required.issubset(data.columns): raise ValueError(f'missing {required-set(data.columns)}')
    df=data.copy();df['date']=pd.to_datetime(df['date'])
    if df.duplicated(['date','site_id']).any(): raise ValueError('duplicate site/day records')
    if (df['units']<0).any(): raise ValueError('units must be nonnegative')
    df=df.sort_values(['site_id','date']).reset_index(drop=True)
    g=df.groupby('site_id')['units']
    df['lag_1']=g.shift(1);df['lag_7']=g.shift(7)
    for n in (7,28):
        df[f'rolling_{n}']=df.groupby('site_id')['units'].transform(lambda s:s.shift(1).rolling(n,min_periods=n).mean())
    df['day_of_week']=df['date'].dt.dayofweek
    df['month']=df['date'].dt.month
    df['is_weekend']=(df['day_of_week']>=5).astype(int)
    return df.dropna().reset_index(drop=True)

def walk_forward(df:pd.DataFrame,folds:int=3,horizon:int=14)->dict:
    prepared=features(df)
    dates=sorted(prepared.date.unique())
    if len(dates)<(folds+1)*horizon+25:
        raise ValueError('not enough history for requested walk-forward windows')
    report=[]
    for fold in range(folds):
        # Training window grows; each test window is strictly after training.
        test_end=len(dates)-(folds-1-fold)*horizon
        train_end=test_end-horizon
        train=prepared[prepared.date<dates[train_end]]
        test=prepared[(prepared.date>=dates[train_end])&(prepared.date<dates[test_end] if test_end<len(dates) else True)]
        model=HistGradientBoostingRegressor(max_iter=90,max_leaf_nodes=12,l2_regularization=3,random_state=42)
        model.fit(train[FEATURES],train.units)
        pred=np.maximum(0,model.predict(test[FEATURES]))
        baseline=np.maximum(0,test.lag_7.to_numpy())
        report.append({'fold':fold+1,'train_through':str(train.date.max().date()),
                       'test_from':str(test.date.min().date()),'test_through':str(test.date.max().date()),
                       'samples':len(test),'model_mae':round(mean_absolute_error(test.units,pred),3),
                       'baseline_mae':round(mean_absolute_error(test.units,baseline),3),
                       'model_rmse':round(float(np.sqrt(mean_squared_error(test.units,pred))),3)})
    return {'dataset':'synthetic, seeded; not operational records', 'target':'next-day units, using observed prior-day history',
            'folds':report,'mean_model_mae':round(float(np.mean([x['model_mae'] for x in report])),3),
            'mean_baseline_mae':round(float(np.mean([x['baseline_mae'] for x in report])),3)}

def save_demo(path: str | Path)->dict:
    metrics=walk_forward(make_demo_data())
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(metrics,indent=2)+'\n')
    return metrics
