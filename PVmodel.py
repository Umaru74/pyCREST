# Based on models and data from:
# [1] G. Masters, Renewable and Efficient Electric Power Systems, John Wiley & Sons, New Jersey, 2004.
# [2] C. Honsberg, S. Bowden, PVEducation.org, http://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time (Consulted 1st December, 2010)
# [3] D. Yogi Goswami, F. Kreith, J. F. Krieder, Principles of Solar Engineering, 2nd Edition Taylor & Francis, 2000.
# [4] D. Dusabe, J. Munda, A. Jimoh, Modelling of Cloudless Solar Radiation for PV Module Performance Analysis, Journal of Electrical Engineering 60 (4) 2009 192-197
# [5] Australian Government, The Equation of Time, http://www.ips.gov.au/Category/Educational/The%20Sun%20and%20Solar%20Activity/General%20Info/EquationOfTime.pdf (Consulted 1st December, 2010).
# [6] A. Skartveit, J. A. Olseth, The probability density and autocorrelation of short-term global and beam irradiance, Solar Energy 49 (6) 477-487.

from math import sin, cos, tan, asin, acos, radians, degrees, exp, inf
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg' if you have PyQt installed
import matplotlib.pyplot as plt


def PVmodel_calculator(hour, minutes):
    local_time_hour = hour
    local_time_minutes = minutes
    latitude = 55.38  # UK's latitude, range(-90, 90)
    longitude = -3.44  # UK's latitude, range(-180, 180)
    day_of_the_year = 150  # range(1,365)
    day_of_the_year_that_summer_time_starts = 90  # Time go forward 1hour around the end of March in UK
    day_of_the_year_that_summer_time_ends = 300  # Time go back 1hour around the end of October in UK
    slope_of_panel = 35  # default angle, range(0, 90)
    azimuth_of_panel = 0  # 180 = North, 0 = South, 90 = East, -90 = West
    ground_reflectance = 0.2  # default value, range(0, 1)
    panel_area = 1  # default value, unit(m^2), range(0, inf)
    system_efficiency = 0.1  # default value, range(0, 1)
    extraterrestrial_radiation = 1200
    
    local_standard_time_hour = (local_time_hour - 1 if
                                day_of_the_year_that_summer_time_starts <= day_of_the_year < day_of_the_year_that_summer_time_ends
                                else local_time_hour)
    local_standard_time_minute = local_time_minutes
    local_standard_time_meridian = 0
    b_value = float(360 * (day_of_the_year - 81) / 364)
    equation_of_time = (9.87 * sin(2 * radians(b_value))) - (7.53 * cos(radians(b_value))) - (
            1.5 * sin(radians(b_value)))
    time_correction_factor = (4 * (longitude - local_standard_time_meridian)) + equation_of_time
    hours_before_solar_noon = 12 - (
            local_standard_time_hour + (local_standard_time_minute / 60) + (time_correction_factor / 60))
    optical_depth = 0.174 + (0.035 * sin(radians(360 * (day_of_the_year - 100) / 365)))
    hour_angle = 15 * hours_before_solar_noon
    declination_delta = 23.45 * sin(radians(360 * (284 + day_of_the_year) / 365.25))
    solar_altitude_angle_beta = degrees(
        asin(
            cos(radians(latitude)) * cos(radians(declination_delta)) * cos(radians(hour_angle)) +
            sin(radians(latitude)) * sin(radians(declination_delta))))
    azimuth_sun_theta = degrees(
        asin(cos(radians(declination_delta)) * sin(radians(hour_angle)) / cos(radians(solar_altitude_angle_beta))))
    azimuth_angle_test = (
        0 if cos(radians(hour_angle) >= (tan(radians(declination_delta)) / tan(radians(radians(longitude))))) else 1)
    adjusted_azimuth_of_sun_theta = (
        azimuth_sun_theta - 90 if azimuth_angle_test == 0 and azimuth_sun_theta > 90 else
        azimuth_sun_theta + 90 if azimuth_angle_test == 0 and azimuth_sun_theta < -90 else
        azimuth_sun_theta if azimuth_angle_test == 0 else
        180 - azimuth_sun_theta if 0 < azimuth_sun_theta < 90 else
        -180 - azimuth_sun_theta if -90 < azimuth_sun_theta < 0 else
        azimuth_sun_theta)
    solar_incident_angle_on_panel = degrees(
        acos(
            cos(radians(solar_altitude_angle_beta)) *
            cos(radians(adjusted_azimuth_of_sun_theta - azimuth_of_panel)) *
            sin(radians(slope_of_panel)) +
            sin(radians(solar_altitude_angle_beta)) * cos(radians(slope_of_panel))))
    clear_sky_beam_radiation_at_surface_horizontal = (
        extraterrestrial_radiation
        * exp((0 - optical_depth) / sin(radians(solar_altitude_angle_beta)))
        if radians(solar_altitude_angle_beta) > 0
        else 0)
    direct_beam_radiation_on_panel = (
        0
        if abs(solar_incident_angle_on_panel) > 90
        else clear_sky_beam_radiation_at_surface_horizontal
             * cos(radians(solar_incident_angle_on_panel)))
    sky_diffuse_factor = 0.095 + (0.04 * sin(radians(360 * (day_of_the_year - 100) / 365)))
    diffuse_radiation_on_panel = (sky_diffuse_factor * clear_sky_beam_radiation_at_surface_horizontal *
                                  ((1 + cos(radians(slope_of_panel))) / 2))
    reflected_radiation_on_panel = (ground_reflectance * clear_sky_beam_radiation_at_surface_horizontal *
                                    (sin(radians(solar_altitude_angle_beta)) + sky_diffuse_factor) *
                                    (1 - cos(radians(slope_of_panel))) / 2)
    total_radiation_on_panel = direct_beam_radiation_on_panel + diffuse_radiation_on_panel + reflected_radiation_on_panel
    
    return clear_sky_beam_radiation_at_surface_horizontal, total_radiation_on_panel

def PVmodel():
    rows = []
    clearness_index = []
    file_path = "C:/Users/Mark/Documents/GitHub/pyCREST/PVmodel.tmp.csv"
    
    for h in range(0, 24):  # h = 1..23
        for m in range(0, 60):  # m = 0..59
            time_str = f"{h:02d}:{m:02d}"
            clear_sky_beam_radiation_at_surface, total_radiation_on_panel = PVmodel_calculator(h, m)
            rows.append([time_str, clear_sky_beam_radiation_at_surface, total_radiation_on_panel])
    
    df = pd.DataFrame(rows, columns=['Time', 'Clear Sky Beam Radiation', 'Total radiation on panel'])
    
    irradiance_df = pd.read_csv("irradiance.csv", index_col=0)
    irradiance_matrix = irradiance_df.to_numpy()
    clearness_index.append(1.0)
    iCurrentStateBin = 101  # start with clear sky
    
    for iTimeStep in range(1, 1440):  # 1min resolution for a day
        fRand = np.random.rand()  # random number between 0 and 1
        fCumulativeP = 0  # reset the cumulative probability count
        
        for i in range(0, 101):  # i = 0..100 in python index, checking the corresponding row
            fCumulativeP += irradiance_matrix[iCurrentStateBin - 1][i]
            
            if fRand <= fCumulativeP:
                iCurrentStateBin = i + 1  # convert to python index
                break
        
        # convert bin index to clearness index
        dk = 1 if iCurrentStateBin == 101 else round(((iCurrentStateBin / 100) - 0.01), 2)
        clearness_index.append(dk)
    
    df['Clearness index'] = clearness_index
    df['Outdoor global irradiance'] = df['Clear Sky Beam Radiation'] * df['Clearness index']
    df['Net radiation on panel (W/m^2)'] = df['Total radiation on panel'] * df['Clearness index']
    
    fig, ax = plt.subplots(figsize=(12, 4))
    
    # Use step plots to keep each value constant until the next timestamp
    ax.step(df['Time'], df['Clear Sky Beam Radiation'], where='post', label='Clear Sky Beam Radiation')
    ax.step(df['Time'], df['Total radiation on panel'], where='post', label='Total radiation on panel')
    ax.step(df['Time'], df['Net radiation on panel (W/m^2)'], where='post', label='Net radiation on panel')
    
    ax.set_xlabel('Time')
    ax.set_ylabel('W / m^2', labelpad=5)
    ax.grid(True)
    ax.legend()
    
    # X-axis ticks every 1 hour
    xticks = range(0, 1441,
                   60)  # 0, 60, 120, ..., 1440 (10-sec resolution → 1 min = 6 points, but for labels use hours)
    xticklabels = [f"{h:02d}:00" for h in range(0, 25)]  # 0:00 to 24:00
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels)
    ax.set_xlim(0, 1440)
    
    plt.tight_layout()
    
    # Return figure and axis so main.py can handle showing/saving
    return df['Outdoor global irradiance'], fig, ax
