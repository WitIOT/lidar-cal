import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


OFFSET_TRIGGER_TIME = 9.854e-6


for folder in os.scandir("./"):
    if folder.is_dir():
        x = None
        y = []
        for file in os.scandir(folder):
            if file.name.startswith("C2") and file.name.endswith(".csv"):
                dt_b = pd.read_csv(file.path, skiprows=4)
                dt_b = dt_b[dt_b["Time"] > OFFSET_TRIGGER_TIME]
                dt_b["Distacne"] = 3e8 * (dt_b["Time"] / 2)
                row = dt_b.head(1)
                dt_b["Distacne2"] = (dt_b["Distacne"]) ** 2
                dt_b["R2"] = dt_b["Ampl"] * dt_b["Distacne2"]
                dt_b["d2p"] = dt_b["Distacne"] - row["Distacne"].values[0]
                y.append(dt_b["R2"].values * -1)
                if x is None:
                    x = dt_b["d2p"].values
            if file.name.startswith("MPL") and file.name.endswith(".csv"):
                dt_mpl = pd.read_csv(
                    file.path,
                    usecols=["range_raw", "copol_raw"],
                )
                dt_mpl = dt_mpl[dt_mpl["range_raw"] * 1000 < 3750]
                norm_co = dt_mpl["copol_raw"] / np.max(dt_mpl["copol_raw"])
                mpl = dt_mpl["range_raw"] * 1000

        plt.figure(dpi=100, figsize=(8, 10))
        d2p = np.average(np.array(y), 0)
        norm = d2p / np.max(d2p)
        plt.plot(norm, x, label="Oscilloscope", c="FireBrick")
        plt.plot(norm_co, mpl, label="Lidar MPL", c="DodgerBlue")
        plt.ylabel("Distance (m)")
        plt.xlabel("Digitizer Signal (v*s\u00b2)")
        plt.legend()
        plt.title(f"Oscilloscope VS Lidar MPL {folder.name}")
