import csv

class Employee:
    def __init__(self, id, name, roles, open, close, max_hours):
        self.id = id
        self.name = name
        self.roles = roles
        self.open = open
        self.close = close
        self.max_hours = max_hours

    def can_work_role(self, role):
        return role in self.roles

    def is_available(self, start, end):
        return self.open <= start and end <= self.close

    def can_work_hours(self, hours):
        return 0 <= hours <= self.max_hours

    def role_count(self):
        return len(self.roles)

def convert_time(time_string):
    hours, minutes = map(int, time_string.split(":"))
    return hours + minutes / 60

def load_employees(filename):
    employees = []

    with open(filename, "r", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            employee = Employee(
                int(row["id"]),
                row["name"],
                row["roles"].split("|"),
                convert_time(row["available_start"]),
                convert_time(row["available_end"]),
                float(row["max_hours"])
            )

            employees.append(employee)

    return employees
