import matplotlib

matplotlib.use("TkAgg")  # switch backend to TkAgg
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
from OccupancySimulation import RunOccupancySimulation

def plotOccupancySimulation():
    # Load active occupancy data
    df, iResidents, day_type = RunOccupancySimulation()

    x = np.linspace(0, 24, 144)  # 24 hours, 10-min resolution

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 4))

    # Step plot for active occupancy
    ax.step(x, df, where='post', linewidth=2.5)

    # Labels and title
    ax.set_xlabel("Time")
    ax.set_ylabel("# of active occupants")
    ax.set_title(f"Active Occupancy Profile\nNumber of Occupants: {iResidents}  :  {day_type}")

    # Grid and x-axis ticks
    ax.grid(True)
    ax.set_xticks([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24])
    ax.set_xticklabels([
        "00:00", "01:00", "02:00", "03:00", "04:00", "05:00", "06:00", "07:00", "08:00", "09:00",
        "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00",
        "20:00", "21:00", "22:00", "23:00", "24:00"
    ])
    ax.set_xlim(0, 24)
    ax.yaxis.set_major_locator(MultipleLocator(1))
    plt.tight_layout()

    # Return figure and axis for external control
    return fig, ax, df, iResidents, day_type

