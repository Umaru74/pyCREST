import builtins
import csv

file_path = r"C:\Users\Mark\Documents\GitHub\pyCREST\test.csv"


with builtins.open(file_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "value"])
    writer.writerow(["test", 456])
    
print("CSV updated successfully")