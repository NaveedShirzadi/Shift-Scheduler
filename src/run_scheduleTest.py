# Connects the teammates' file reader (employee.py) to the scheduler (scheduler.py)
from employee import Employee, load_employees          # teammate: reads employee_list.csv
import schedulerTesting                            # my part: builds the schedule + breaks


def runFromCsv(csvFile, openTime, closeTime, roleList):
    loaded = load_employees(csvFile)
    return schedulerTesting.run(openTime, closeTime, .5, roleList, loaded)


if __name__ == "__main__":
    # Role names must match the CSV spelling exactly: "cook", "cashier", "drive_thru"
    needs = [
        {"role": "cook",       "count": 2, "openInterval": 10, "closeInterval": 17},
        {"role": "cashier",    "count": 1, "openInterval": 10, "closeInterval": 13},
        {"role": "cashier",     "count": 2, "openInterval": 13, "closeInterval": 17},
        {"role": "drive_thru", "count": 1, "openInterval": 10, "closeInterval": 17},
    ]
    runFromCsv("employee_list.csv", 10, 17, needs)