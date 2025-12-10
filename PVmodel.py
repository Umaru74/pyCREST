# Based on models and data from:
# [1] G. Masters, Renewable and Efficient Electric Power Systems, John Wiley & Sons, New Jersey, 2004.
# [2] C. Honsberg, S. Bowden, PVEducation.org, http://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time (Consulted 1st December, 2010)
# [3] D. Yogi Goswami, F. Kreith, J. F. Krieder, Principles of Solar Engineering, 2nd Edition Taylor & Francis, 2000.
# [4] D. Dusabe, J. Munda, A. Jimoh, Modelling of Cloudless Solar Radiation for PV Module Performance Analysis, Journal of Electrical Engineering 60 (4) 2009 192-197
# [5] Australian Government, The Equation of Time, http://www.ips.gov.au/Category/Educational/The%20Sun%20and%20Solar%20Activity/General%20Info/EquationOfTime.pdf (Consulted 1st December, 2010).
# [6] A. Skartveit, J. A. Olseth, The probability density and autocorrelation of short-term global and beam irradiance, Solar Energy 49 (6) 477-487.

from math import sin, cos, tan, asin, acos, radians, degrees, exp, inf
import pandas as pd


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


# def get_float_input(prompt, min_val, max_val):
#     while True:
#         try:
#             value = float(input(prompt))
#             if min_val <= value <= max_val:
#                 return value
#             else:
#                 print(f"Error: Please enter a value between {min_val} and {max_val}")
#         except ValueError:
#             print("Error: Please enter a valid float number")
#
#
# def get_int_input(prompt, min_val, max_val):
#     while True:
#         try:
#             value = int(input(prompt))
#             if min_val <= value <= max_val:
#                 return value
#             else:
#                 print(f"Error: Please enter a value between {min_val} and {max_val}")
#         except ValueError:
#             print("Error: Please enter a valid int number")

# Step-2: Calculating other variables based on the user inputs


# print(B_value)
# print(Equation_of_time)
# print(Time_correction_factor)
# print(Hours_before_solar_noon)
# print(Optical_depth)
# print(Declination_delta)
# print(Solar_altitude_angle_beta)
# print(Azimuth_sun_theta)
# print(Azimuth_angle_test)
# print(Adjusted_azimuth_of_sun_theta)
# print(Solar_incident_angle_on_panel)
# print(Clear_sky_beam_radiation_at_surface_horizontal)
# print(Direct_beam_radiation_on_panel)
# print(Sky_diffuse_factor)
# print(Diffuse_radiation_on_panel)
# print(Reflected_radiation_on_panel)
# print(Total_radiation_on_panel)

rows = []
for h in range(12, 15):
    for m in range(0, 20):
        time_str = f"{h:02d}:{m:02d}"
        clear_sky_beam_radiation_at_surface, total_radiation_on_panel = PVmodel_calculator(h, m)
        rows.append([time_str, clear_sky_beam_radiation_at_surface, total_radiation_on_panel])
        
df = pd.DataFrame(rows, columns=['Time', 'Clear Sky Beam Radiation', 'Total radiation on panel'])
df.to_csv(r"C:\Users\Mark\Desktop\PVmodel_test.csv", index=False)
print("Saved successfully!")