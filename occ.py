import pandas as pd
import matplotlib
matplotlib.use("TkAgg")  # switch backend to TkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from OccupancySimulation import RunOccupancySimulation


#Load active occupancy data from the above file
df, iResidents, day_type = RunOccupancySimulation()

x = np.linspace(0,24,144)

#plot

plt.figure(figsize=(12,5))
plt.step(x, df, where='post', linewidth=2.5)  # 'post' keeps step at current value
plt.xlabel("Time")
plt.ylabel("# of active occupants")
plt.title("Active Occupancy Profile \n"
          "Number of Occupants:" + str(iResidents) + "  :  " +str(day_type))
plt.grid(True)
plt.xticks([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24],
           ["00:00", "02:00", "04:00", "06:00", "08:00", "10:00",
            "12:00", "14:00", "16:00", "18:00", "20:00", "22:00","24:00"])
plt.xlim(0,24)
plt.gca().yaxis.set_major_locator(MultipleLocator(1))
plt.show()





