from pathlib import Path
import csv 

file_path = Path(__file__).parent / "employee_list.csv"             

with open(file_path) as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for line in csv_reader:
        line['id'] = int(line['id'])                                # Converts String 'id' back to Int
        line['max_hours'] = float(line['max_hours'])                # Converts the String Value of 'max_hours' into float number    
        line['roles'] = line['roles'].split("|")                    # Changes the roles to be a list containing # of roles of an employee
        print(line)



   
