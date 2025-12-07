import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

def RunOccupancySimulation():
    #Step 1 - user input: maximum occupancy number, weekdays or weekend
    
    while True:
        try:
            iResidents = int(input("How many residents? (1 to 5)"))
            if 1 <= iResidents <= 5:
                break #valid input -> exit the loop
            else:
                print("Error: Please enter an integer between 1 and 5")
        except ValueError:
            print("Error: Please enter a valid integer")
            
    while True:
        day_type = input("Is it a weekday or weekend (enter 'weekday' or weekend')").strip().lower()
        if day_type in ["weekday", "weekend"]:
            break
        else:
            print("Error: Please type 'weekday' or 'weekend'")
    
    #Step 2 - Determine the initial active occupancy number between 00:00 and 00:10
    
    ##grabbing the corresponding data file
    if day_type == "weekday":
        start_state_file = "weekday_start_states.dat"
    elif day_type == "weekend":
        start_state_file = "weekend_start_states.dat"
    else:
        print("Error:")
        
    df_start_state = pd.read_csv(start_state_file,sep='\t', skiprows=21, header=None)
    df_start_state.columns = ["1", "2", "3", "4", "5", "6"]
    
    prob_column = df_start_state[str(iResidents)].values.astype(float)
    prob_sum = prob_column.sum()
    if prob_sum == 0:
        raise ValueError("Error: probability column sums to zero. Check data file.")
    
    prob_column = prob_column / prob_sum  # Now sums to exactly 1
    
    ##determining the initial active occupancy number depending on the given probability
    initial_occupant_number = np.arange(len(prob_column))
    initial_occupants = np.random.choice(initial_occupant_number, p = prob_column)
    
    #Step 3 - Determine the active occupancy transition for each ten minutes period of the day
    
    ##grabbing the corresponding transition matrix
    suffix = "wd" if day_type == "weekday" else "we"
    occ_trans_file_path = f"tpm{iResidents}_{suffix}.dat"
    
    df_occ_trans_matrix = pd.read_csv(occ_trans_file_path, sep='\t', skiprows=22, header=None)
    df_occ_trans_matrix.columns = ["10min_count", "current_act_occ_number", "prob_trans_to_0", "prob_trans_to_1",
                                   "prob_trans_to_2", "prob_trans_to_3", "prob_trans_to_4", "prob_trans_to_5",
                                   "prob_trans_to_6"]
    occ_profile = []
    occ_next = initial_occupants
    for i in range(1, 145):
     
        occ_profile.append(occ_next)
        #pd.set_option('display.max_columns', None) to see the whole matrix
        #pd.set_option('display.width', None)
        
        #grabbing the corresponding matrix
        df_current_occ_trans_matrix = df_occ_trans_matrix.iloc[7*(i-1):7*(i-1)+7, 0:9]
        
        df_current_occ_trans_matrix_corres_row = df_current_occ_trans_matrix[df_current_occ_trans_matrix['current_act_occ_number'] == occ_next]
        prob_row = df_current_occ_trans_matrix_corres_row.iloc[:, 2:]
        prob_row = prob_row.to_numpy().flatten()
        prob_row = prob_row / prob_row.sum()
        occ_next = np.random.choice(7, p = prob_row)
        print(occ_profile)
    
    #Step 4 - Update the occ_sim_data
    
    file_path = Path("C:/Users/Mark/Documents/GitHub/pyCREST/occ_sim_data.txt")
    
    try:
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist")
        
        # Read file
        lines = file_path.read_text().splitlines()
        print(f"Read {len(lines)} lines from {file_path.name}")
        
        # Update lines
        for i, k in zip(range(7, 150), range(len(occ_profile))):
            parts = lines[i].split()
            if len(parts) < 3:
                raise ValueError(f"Line {i} does not have enough columns: {parts}")
            parts[2] = str(occ_profile[k])
            lines[i] = "\t".join(parts)
        
        # Write back
        file_path.write_text("\n".join(lines) + "\n")
        print("File updated successfully.")
    
    except Exception as e:
        print(f"Error: {e}")


RunOccupancySimulation()


