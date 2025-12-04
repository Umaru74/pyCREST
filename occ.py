#This script is for making active occupany graph at 10 min resolution

import pandas as pd
import matplotlib
matplotlib.use("TkAgg")  # switch backend to TkAgg
import matplotlib.pyplot as plt
import numpy as np


file_path = 'occ_sim_data'

#Load active occupancy data from the above file

df = pd.read_csv("occ_sim_data", sep='\t', skiprows=6, header=None, )
df.columns = ["10minutes_count", "Time", "Occupants"]

x = np.linspace(0,24,144)


#plot

plt.figure(figsize=(12,5))
plt.plot(x, df["Occupants"], linestyle='-', linewidth=2.5)
plt.xlabel("Time")
plt.ylabel("# of active occupancy")
plt.title("Active Occupancy")
plt.grid(True)
plt.xticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
           ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00", "22:00","24:00"])
plt.xlim(0,24)
plt.show()





