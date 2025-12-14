import pandas as pd
import numpy as np
import random
import math
import time
from PVmodel import PVmodel
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from occ import plotOccupancySimulation


def getMonteCarloNormalDistribution(mean, sd):  # sd: standard deviation
    
    if mean == 0:
        return 0
    
    bOK = False
    iGuess = 0
    
    while not bOK:
        # generate a random guess within mean +/- 4*SD
        iGuess = int(random.random() * (sd * 8) - (sd * 4) + mean)
        
        #  normal PDF (probability density function)
        px = (1 / (sd * math.sqrt(2 * math.pi))) * math.exp(-((iGuess - mean) ** 2) / (2 * sd ** 2))
        
        if px >= random.random():
            bOK = True
    
    return iGuess


def getRelativeUseWeight():  # representing the concept that some bulbs are used more frequently than others
    calibration_scalar = 0.0081537  # Used to calibrate the model so that it provides a particular average output over a
    # large number of runs
    return - calibration_scalar * math.log(random.uniform(1e-10, 1))


def getLightDuration():  # gives lighting duration in minutes
    r1 = random.random()  # random number between 0 and 1
    bin_index = 0
    for j, cml in enumerate(cml_prob):
        if r1 < cml:
            bin_index = j
    r2 = random.random()
    duration = int((r2 * (upper[bin_index] - lower[bin_index]))) + lower[bin_index]
    return duration

def get10secProb(fCalibrated, effectiveOcc):
    if effectiveOcc == 0:
        return 0.0
    prob_old = fCalibrated * effectiveOcc
    prob_new = 1 - (1 - prob_old)**(1 / 6)
    return prob_new
    
# ---------------------------------------------
#  default input
# ---------------------------------------------

mean_external_global_irradiance_threshold = 60
sd_external_global_irradiance_threshold = 10
irradiance_threshold = getMonteCarloNormalDistribution(mean_external_global_irradiance_threshold,
                                                       sd_external_global_irradiance_threshold)

# ---------------------------------------------
# Light duration bins
# ---------------------------------------------
lower = np.array([1, 2, 3, 5, 9, 17, 28, 50, 92])  # Lower bounds of duration (minutes)
upper = np.array([1, 2, 4, 8, 16, 27, 49, 91, 259])  # Upper bounds of duration (minutes)
cml_prob = np.array([0.111111111, 0.222222222, 0.333333333, 0.444444444,
                     0.555555556, 0.666666667, 0.777777778, 0.888888889, 1.0])  # Cumulative probability for each bin

# ---------------------------------------------
#  reading occupancy and irradiance data
# ---------------------------------------------
outdoor_irradiance_profile, fig_PVmodel, ax_PVmodel = PVmodel()
fig_occmodel, ax_occmodel, occ_profile, iResidents, day_type = plotOccupancySimulation()

# ---------------------------------------------
#  changing the resolution of "occ_profile" and "outdoor_irradiance_profile", update to effective occupancy
# ---------------------------------------------
effective_occupancy_mapping = {0: 0, 1: 1, 2: 1.528, 3: 1.694, 4: 1.983, 5: 2.094}  # effective occupancy
occ_profile = np.vectorize(effective_occupancy_mapping.get, otypes=[float])(occ_profile)  # updating occupancy profile
occ_profile_10sec_resolution = np.repeat(occ_profile, 60)  # 10min -> 10 sec resolution
row_repeat = outdoor_irradiance_profile.values
outdoor_irradiance_profile_10sec_resolution = np.repeat(row_repeat, 6)  # 1min -> 10 sec resolution

# ---------------------------------------------
#  adding a relative use weight for each bulb to the data frame
# ---------------------------------------------

# ---------------------------------------------
#  creating a base data frame for bulb number & power rating
# ---------------------------------------------
df = pd.read_csv("bulbs.dat", sep='\t', header=None, skiprows=14)  # read house data with bulbs config
house_number = random.randint(1, 100)  # Choose a random house from "bulbs.dat"
bulbs_config = df[df.iloc[:, 0] == house_number]  # grab the bulbs config corresponding to the house number
bulbs_config = bulbs_config.iloc[:, 2:]  # removing the second column "bulbs number
bulbs_config.index = ['Power rating']
bulbs_config.columns = range(1, len(bulbs_config.columns) + 1)
bulb_config = bulbs_config.fillna(0, inplace=True)  # replacing Nan with 0
calibration_value_row = []
for i in range(len(bulbs_config.columns)):
    calibration_value_row.append(getRelativeUseWeight())
pd.set_option('display.max_columns', None)
print(f"House Number:{house_number}")
bulbs_config.loc['Calibrated relative use weight'] = calibration_value_row
# print(bulbs_config)
bulb_calUseWeight = bulbs_config.loc['Calibrated relative use weight']
bulb_power_rate = bulbs_config.loc['Power rating']
# print(bulb_power_rate)
# print(bulb_calUseWeight.iloc[0])
# print(bulb_power_rate.iloc[0])
# print(bulb_power_rate.iloc[1])


while len(bulbs_config) < 8642:
    bulbs_config.loc[len(bulbs_config)] = [0] * len(bulbs_config.columns)

time_index = pd.date_range(start="00:00:00", periods=8640, freq="10s")
time_labels = [t.strftime("%H:%M:%S") for t in time_index]

new_index = ['Power rating', 'Calibrated relative use weight'] + time_labels
bulbs_config.index = new_index
# ---------------------------------------------
#  simulate 10 sec by 10 sec for each bulb
# ---------------------------------------------
for bulbs in (bulbs_config.columns - 1):  # going through each bulb
    iTime = 1
    row_bulb_power = []
    ratedPower = bulb_power_rate.iloc[bulbs]
    while iTime <= 8640:  # simulate every 10 seconds for a day
        irradiance = outdoor_irradiance_profile_10sec_resolution[iTime - 1]  # irradiance at each 10sec resolution
        effective_occupants = occ_profile_10sec_resolution[iTime - 1]  # effective occupants
        isOutsideDarkEnough = irradiance < irradiance_threshold or random.random() < 0.05
        bulb_relUseWeight = bulb_calUseWeight.iloc[bulbs - 1]  # corresponding bulb relative use weight
        
        new_prob = get10secProb(effective_occupants, bulb_relUseWeight)  # calculate prob for 10sec resolution
        if isOutsideDarkEnough and random.random() < new_prob:  # switch-on condition
            light_duration = getLightDuration() * 6  # get the duration of light turning on (count in 10sec)
            
            for j in range(light_duration):
                if iTime > 8640:
                    break
                elif occ_profile_10sec_resolution[iTime - 1] == 0:
                    break
                else:
                    row_bulb_power.append(ratedPower)
                    iTime += 1
        
        else:
            row_bulb_power.append(0)
            iTime += 1
    # print(f"bulb power rating: {ratedPower}")
    # print(row_bulb_power)
    
    bulbs_config.iloc[2:, bulbs] = row_bulb_power
#
# print(bulbs_config)

sim_data = bulbs_config.iloc[2:, :].astype(float)
sim_data['Total Power'] = sim_data.sum(axis=1)
ave = sim_data['Total Power'].mean()

# Convert index to datetime
sim_data.index = pd.to_datetime(sim_data.index, format='%H:%M:%S')

plt.figure(figsize=(12, 4))
plt.step(sim_data.index, sim_data['Total Power'], where='post', color='orange', linewidth=1)
plt.title("Household Lighting Load Profile (10-sec resolution)\n"
          f"Average Lighting Load: {ave.round(decimals=2)} W")
plt.xlabel("Time of Day")
plt.ylabel("Total Power (W)")
plt.grid(True)

ax = plt.gca()
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.set_xlim(sim_data.index[0], sim_data.index[-1])
plt.tight_layout()
plt.show()
