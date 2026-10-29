from employee import Employee, load_employees

# Test 1: Create an employee manually
employee1 = Employee(
    1,
    "Daniel",
    ["cook"],
    9,
    17,
    8
)

print(employee1.name)
print(employee1.roles)
print(employee1.open)
print(employee1.max_hours)

# Test 2: Check employee qualifications
print(employee1.can_work_role("cook"))
print(employee1.can_work_role("cashier"))

# Test 3: Check employee availability
print(employee1.is_available(9, 9.5))
print(employee1.is_available(12, 12.5))
print(employee1.is_available(17, 17.5))

# Test 4: Check maximum working hours
print(employee1.can_work_hours(4))
print(employee1.can_work_hours(8))
print(employee1.can_work_hours(9))

# Test 5: Count qualified roles
print(employee1.role_count())

# Test 6: Load all employees from Alberto's CSV
employees = load_employees("employee_list.csv")

print("\nEmployees loaded:", len(employees))

for employee in employees:
    print(
        employee.id,
        employee.name,
        employee.roles,
        employee.open,
        employee.close,
        employee.max_hours
    )

print("\nAdditional Employee Tests")

ana = employees[1]
sofia = employees[3]

print("Ana can cook:", ana.can_work_role("cook"))
print("Ana can cashier:", ana.can_work_role("cashier"))
print("Ana role count:", ana.role_count())

print("Sofia available 14:30-15:00:",
      sofia.is_available(14.5, 15))

print("Sofia available 15:00-15:30:",
      sofia.is_available(15, 15.5))

print("Sofia can work 7 hours:",
      sofia.can_work_hours(7))
