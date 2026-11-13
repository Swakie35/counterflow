from counterflow.pipeline import make_demo_data,features,walk_forward

def test_deterministic():
    assert make_demo_data(seed=1).equals(make_demo_data(seed=1))

def test_features_use_only_prior_targets():
    df=make_demo_data(days=70,sites=1)
    before=features(df)
    df.loc[df.index[-1],'units']=10000
    after=features(df)
    assert before.iloc[-1].lag_1==after.iloc[-1].lag_1
    assert before.iloc[-1].rolling_28==after.iloc[-1].rolling_28

def test_temporal_folds():
    r=walk_forward(make_demo_data(days=125,sites=2),folds=2,horizon=10)
    assert len(r['folds'])==2
    assert all(f['train_through']<f['test_from'] for f in r['folds'])
    assert r['mean_model_mae']>=0

def test_bad_input():
    import pytest
    with pytest.raises(ValueError):make_demo_data(days=5)
