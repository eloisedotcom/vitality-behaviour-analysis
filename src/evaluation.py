import numpy as np
import matplotlib.pyplot as plt
from sklearn.calibration import calibration_curve

def plot_calibration(y_true, proba, title="Calibration (Wed-cutoff model)"):
    frac_pos, mean_pred = calibration_curve(y_true, proba, n_bins=10, strategy="quantile")
    plt.figure(figsize=(4,4))
    plt.plot([0,1],[0,1], "--", color="gray", label="perfect")
    plt.plot(mean_pred, frac_pos, marker="o", label="model")
    plt.xlabel("Predicted probability")
    plt.ylabel("Observed frequency")
    plt.title(title)
    plt.legend()
    plt.tight_layout()