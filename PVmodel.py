# Based on models and data from:
# [1] G. Masters, Renewable and Efficient Electric Power Systems, John Wiley & Sons, New Jersey, 2004.
# [2] C. Honsberg, S. Bowden, PVEducation.org, http://www.pveducation.org/pvcdrom/properties-of-sunlight/solar-time (Consulted 1st December, 2010)
# [3] D. Yogi Goswami, F. Kreith, J. F. Krieder, Principles of Solar Engineering, 2nd Edition Taylor & Francis, 2000.
# [4] D. Dusabe, J. Munda, A. Jimoh, Modelling of Cloudless Solar Radiation for PV Module Performance Analysis, Journal of Electrical Engineering 60 (4) 2009 192-197
# [5] Australian Government, The Equation of Time, http://www.ips.gov.au/Category/Educational/The%20Sun%20and%20Solar%20Activity/General%20Info/EquationOfTime.pdf (Consulted 1st December, 2010).
# [6] A. Skartveit, J. A. Olseth, The probability density and autocorrelation of short-term global and beam irradiance, Solar Energy 49 (6) 477-487.

from math import sin, cos, tan, asin, acos, radians, degrees, exp


def get_float_input(prompt, min_val, max_val):
    while True:
        try:
            value = float(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Error: Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("Error: Please enter a valid float number")


def get_int_input(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
            else:
                print(f"Error: Please enter a value between {min_val} and {max_val}")
        except ValueError:
            print("Error: Please enter a valid int number")


# Step-1: User Inputs

Latitude = get_float_input("What is the latitude? (-90 to 90):", -90, 90)
Longitude = get_float_input("What is the longitude? (-180 to 180):", -180, 180)
Day_of_the_year = get_int_input("What is the day of the year? (1 to 365)", 1, 365)
Day_of_the_year_that_summer_time_starts = get_int_input(
    "What is the day of the year that summer time starts? (1 to 365)", 1, 365)
Day_of_the_year_that_summer_time_ends = get_int_input("What is the day of the year that summer time ends? (1 to 365)",
                                                      1, 365)
Slope_of_panel = get_int_input("What is the slope of the panel (0 to 90)", 0,
                               90)  # 0: flat on the ground, 90:vertical wall
Azimuth_of_panel = get_int_input("What is panel azimuth (°) [180 = North, 0 = South, ±90 = East/West]:", -90, 180)

# Step-2: Calculating other variables based on the user inputs

Local_time_hour = 23
Local_time_minute = 59
Extraterrestrial_radiation = 1200
Local_standard_time_hour = (
    Local_time_hour - 1 if Day_of_the_year_that_summer_time_starts <= Day_of_the_year < Day_of_the_year_that_summer_time_ends
    else Local_time_hour)
Local_standard_time_minute = Local_time_minute
Local_standard_time_meridian = 0  #
B_value = float(360 * (Day_of_the_year - 81) / 364)
Equation_of_time = (9.87 * sin(2 * radians(B_value))) - (7.53 * cos(radians(B_value))) - (1.5 * sin(radians(B_value)))
Time_correction_factor = (4 * (Longitude - Local_standard_time_meridian)) + Equation_of_time
Hours_before_solar_noon = 12 - (
            Local_standard_time_hour + (Local_standard_time_minute / 60) + (Time_correction_factor / 60))
Optical_depth = 0.174 + (0.035 * sin(radians(360 * (Day_of_the_year - 100) / 365)))
Hour_angle = 15 * Hours_before_solar_noon
Declination_delta = 23.45 * sin(radians(360 * (284 + Day_of_the_year) / 365.25))
Solar_altitude_angle_beta = degrees(
    asin(
        cos(radians(Latitude)) * cos(radians(Declination_delta)) * cos(radians(Hour_angle)) +
        sin(radians(Latitude)) * sin(radians(Declination_delta))))
Azimuth_sun_theta = degrees(
    asin(cos(radians(Declination_delta)) * sin(radians(Hour_angle)) / cos(radians(Solar_altitude_angle_beta))))
Azimuth_angle_test = (
    0 if cos(radians(Hour_angle) >= (tan(radians(Declination_delta)) / tan(radians(radians(Longitude))))) else 1)
Adjusted_azimuth_of_sun_theta = (
    Azimuth_sun_theta - 90 if Azimuth_angle_test == 0 and Azimuth_sun_theta > 90 else
    Azimuth_sun_theta + 90 if Azimuth_angle_test == 0 and Azimuth_sun_theta < -90 else
    Azimuth_sun_theta if Azimuth_angle_test == 0 else
    180 - Azimuth_sun_theta if 0 < Azimuth_sun_theta < 90 else
    -180 - Azimuth_sun_theta if -90 < Azimuth_sun_theta < 0 else
    Azimuth_sun_theta)
Solar_incident_angle_on_panel = degrees(
    acos(
        cos(radians(Solar_altitude_angle_beta)) *
        cos(radians(Adjusted_azimuth_of_sun_theta - Azimuth_of_panel)) *
        sin(radians(Slope_of_panel)) +
        sin(radians(Solar_altitude_angle_beta)) * cos(radians(Slope_of_panel))))
Clear_sky_beam_radiation_at_surface_horizontal = (
    Extraterrestrial_radiation
    * exp((0 - Optical_depth) / sin(radians(Solar_altitude_angle_beta)))
    if radians(Solar_altitude_angle_beta) > 0
    else 0)
Direct_beam_radiation_on_panel = (
    0
    if abs(Solar_incident_angle_on_panel) > 90
    else Clear_sky_beam_radiation_at_surface_horizontal
         * cos(radians(Solar_incident_angle_on_panel)))
Sky_diffuse_factor = 0.095 + (0.04 * sin(radians(360*(Day_of_the_year-100)/365)))
Diffuse_radiation_on_panel = Sky_diffuse_factor * Clear_sky_beam_radiation_at_surface_horizontal *((1+cos(radians(Slope_of_panel)))/2)
print(B_value)
print(Equation_of_time)
print(Time_correction_factor)
print(Hours_before_solar_noon)
print(Optical_depth)
print(Declination_delta)
print(Solar_altitude_angle_beta)
print(Azimuth_sun_theta)
print(Azimuth_angle_test)
print(Adjusted_azimuth_of_sun_theta)
print(Solar_incident_angle_on_panel)
print(Clear_sky_beam_radiation_at_surface_horizontal)
print(Direct_beam_radiation_on_panel)
print(Sky_diffuse_factor)
print(Diffuse_radiation_on_panel)


