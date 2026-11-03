import csv
from pathlib import Path
from datetime import datetime

file_path = Path(__file__).parent / "employee_list.csv"                                   # Turns Location into a path object

seen_ids = set()                                                                          # Stores employee IDs to check for duplicates
errors = []                                                                               # Stores any validation error messages

with open(file_path, "r", newline="") as csv_file:
    csv_reader = csv.DictReader(csv_file)

    for line in csv_reader:
        name = (line.get("name") or "").strip()                                            # retrieves the employee's name
        raw_id = (line.get("id") or "").strip()                                            # Gets the employee ID as a string and removes extra spaces

        # Check missing or invalid IDs
        try:
            employee_id = int(raw_id)                                                      # Converts the ID string into an integer
            if employee_id <= 0:                                                           # Checks if the ID is zero or negative
                raise ValueError                                                           # Triggers an error for an invalid ID
        except ValueError:                                                                 # Catches invalid ID values
            errors.append(f"{name}: Missing or invalid ID")                                # Records the error message
            employee_id = None                                                             # Marks the ID as invalid

        # Check duplicate IDs
        if employee_id is not None:                                                        # Only checks IDs that passed validation
            if employee_id in seen_ids:                                                    # Checks if the ID was already used
                errors.append(f"{name}: Duplicate ID")                                     # Records the error message
            seen_ids.add(employee_id)

        # Check missing names
        if not name:                                                                       # Checks if the employee name is empty
            errors.append(f"Employee {raw_id}: Missing name")

        # Check missing roles
        roles = (line.get("roles") or "").strip()                                           # Gets the roles and removes extra spaces
        
        if not roles or not any(role.strip() for role in roles.split("|")):                 # Checks if the roles field has at least one nonempty role
            errors.append(f"{name}: Missing roles")

        # Check maximum hours
        try:
            max_hours = float(line.get("max_hours") or "")
            if max_hours <= 0:                                                              # Checks for zero or negative hours
                raise ValueError
        except ValueError:
            errors.append(f"{name}: Invalid maximum hours")

        # Check availability times
        try:
            start = datetime.strptime(
                line.get("available_start") or "", "%H:%M"                                  # Converts the starting time into a datetime object
            )
            end = datetime.strptime(                                                        
                line.get("available_end") or "", "%H:%M"
            )

            if end <= start:                                                                # Checks if the end time is after the start time
                errors.append(f"{name}: Invalid availability range")                        

            if start.minute not in (0, 30) or end.minute not in (0, 30):                    # Checks whether both times follow 30-minute intervals
                errors.append(f"{name}: Times must use 30-minute intervals")

        except ValueError:
            errors.append(f"{name}: Missing or invalid availability")

if errors:
    print("Validation failed:")
    for error in errors:
        print("-", error)
else:
    print("Validation passed!")
    print(f"All {len(seen_ids)} employees have valid data.")