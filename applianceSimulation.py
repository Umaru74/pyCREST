# ----------------------------------------
# Monthly temperature modifier for heating appliance
# ----------------------------------------
month_boundaries = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365]
monthlyRelativeTempMod = [0, 1.63, 1.821, 1.595, 0.867, 0.763, 0.191, 0.156, 0.087, 0.399, 0.936, 1.561, 1.994]


def findMonth(day):  # change input date to the corresponding month
    if not 1 <= day <= 365:
        raise ValueError("Day of the year must be between 1 and 365")
    for i, end_day in enumerate(month_boundaries):
        if day <= end_day:
            month = i
            break
    return month



