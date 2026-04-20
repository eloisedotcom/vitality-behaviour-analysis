from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.calibration import CalibratedClassifierCV

@dataclass
class CostMatrix:
    cost_fp: float = 1.0   # predict will-close but don't → lose weekly reward
    cost_fn: float = 2.0   # predict won't-close but do → unnecessary workouts
    cost_tp: float = 0.0
    cost_tn: float = 0.0

def train_eval_timebased(X: pd.DataFrame, y: pd.DataFrame, features: list[str], cost: CostMatrix):
    data = X.merge(y, on="week")
    data = data.sort_values("week")
    # Simple time split: 70% train, 15% val, 15% test
    n = len(data)
    train_end = int(n*0.7)
    val_end = int(n*0.85)
    train, val, test = data.iloc[:train_end], data.iloc[train_end:val_end], data.iloc[val_end:]

    Xtr, ytr = train[features], train["will_close_week"]
    Xval, yval = val[features], val["will_close_week"]
    Xte, yte = test[features], test["will_close_week"]

    # Baseline heuristic: predict close if wed_points >= 600
    baseline = (Xte["wed_points"] >= 600).astype(int)
    baseline_auc = roc_auc_score(yte, baseline)

    # Logistic + calibration
    base = LogisticRegression(max_iter=200, C=1.0)
    clf = CalibratedClassifierCV(base, method="isotonic", cv=3)
    clf.fit(pd.concat([Xtr, Xval]), pd.concat([ytr, yval]))
    proba = clf.predict_proba(Xte)[:, 1]

    auc = roc_auc_score(yte, proba)
    brier = brier_score_loss(yte, proba)

    # Cost-sensitive threshold selection on validation set
    p_val = clf.predict_proba(Xval)[:, 1]
    thresholds = np.linspace(0.05, 0.95, 19)
    def expected_cost(y_true, p, t, cm: CostMatrix):
        y_hat = (p >= t).astype(int)
        fp = ((y_hat == 1) & (y_true == 0)).sum()
        fn = ((y_hat == 0) & (y_true == 1)).sum()
        tp = ((y_hat == 1) & (y_true == 1)).sum()
        tn = ((y_hat == 0) & (y_true == 0)).sum()
        return cm.cost_fp*fp + cm.cost_fn*fn + cm.cost_tp*tp + cm.cost_tn*tn
    best_t = min(thresholds, key=lambda t: expected_cost(yval.values, p_val, t, cost))

    yhat = (proba >= best_t).astype(int)
    return {
        "features": features,
        "baseline_auc": float(baseline_auc),
        "auc": float(auc),
        "brier": float(brier),
        "best_threshold": float(best_t),
        "test_confusion": {
            "tp": int(((yhat==1)&(yte==1)).sum()),
            "fp": int(((yhat==1)&(yte==0)).sum()),
            "tn": int(((yhat==0)&(yte==0)).sum()),
            "fn": int(((yhat==0)&(yte==1)).sum()),
        }
    }, clf