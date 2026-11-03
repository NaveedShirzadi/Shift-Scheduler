import sys
sys.setrecursionlimit(10000)


MIN_SHIFT_HOURS = 2
MAX_STEPS = 100000
MEAL_TARGETS = [3, 8]
MEAL_DEADLINES = [5, 10]

def mealsRequired(length):
    if length > 10:
        return 2

    if length > 5:
        return 1

    return 0

def canWaiveMeal(n, length, mealsTaken):
    if n == 0:
        return length <= 6

    return length <= 12 and mealsTaken >= 1

def formatTime(t):
    hour = int(t)
    minutes = 30 if t%1 else 0
    hour12 = hour % 12 or 12
    return f"{hour12}:{minutes:02d}"

class Block:
    def __init__(self, blockNum, openTime, closeTime):
        self.blockNum = blockNum
        self.open = openTime
        self.close = closeTime
        self.roles = []
        self.assignments = []
        self.size = closeTime-openTime

    def __str__(self):
        return f"Block {self.blockNum}: {formatTime(self.open)} - {formatTime(self.close)}"

    def isWorking(self, employee):
        return any(e is employee for r, e in self.assignments)


def splitBlocks(sbOpen, sbClose, sbSize):
    blocks = []
    counter = 0

    while sbOpen + (counter * sbSize) < sbClose:
        start = sbOpen + (counter*sbSize)
        blocks.append(Block(counter, start, min(start + sbSize, sbClose)))
        counter+= 1

    return blocks

def addRoles(blocks, roles):
    for role in roles:
        for block in blocks:
            if block.open >= role["openInterval"] and block.close <= role["closeInterval"]:
                for _ in range(role["count"]):
                    block.roles.append(role["role"])


# def checkFit(block, employee):
#     return block.open >= employee.open and block.close <= employee.close

def spanIndex(employee):
    empBlocks = [block.blockNum for block in employee.blocks] + [block.blockNum for block in employee.breaks]
    return (min(empBlocks), max(empBlocks)) if empBlocks else None

def getEligible(block, role, employeeList):
    eligibleEmp = []

    for employee in employeeList:
        empShiftSpan = spanIndex(employee)

        continueCheck = empShiftSpan is None or block.blockNum in (empShiftSpan[0] -1, empShiftSpan[1] + 1)

        if (role in employee.roles and continueCheck and employee.is_available(block.open, block.close) and not block.isWorking(employee) and employee.can_add_block(block.size)):
            eligibleEmp.append(employee)

    return eligibleEmp

def sweepUncovered(blocks, employeeList):
    missing = {}
    for block in blocks:
        # role list for block
        slots = block.roles
        
        # list of candidate employees for each role for that block
        candidates = [[emp for emp in employeeList if rol in emp.roles and emp.is_available(block.open, block.close) ] for rol in slots]

        matchedSlots = {}

        # local function for 
        def tryAssign(slotInd, seen):
            for emp in candidates[slotInd]:
                if emp.id in seen:
                    continue
                seen.add(emp.id)
                if emp.id not in matchedSlots or tryAssign(matchedSlots[emp.id], seen):
                    matchedSlots[emp.id] = slotInd
                    return True
            return False

        for slotInd in range(len(slots)):
            tryAssign(slotInd, set())

        matched = set(matchedSlots.values())

        for slotInd, rol in enumerate(slots):
            if slotInd not in matched:
                missing.setdefault(rol, {}).setdefault(block.blockNum, 0)
                missing[rol][block.blockNum] += 1

    byNum = {blk.blockNum: blk for blk in blocks}
    merged = []

    for role, missDict in missing.items():
        nums = sorted(missDict)
        i = 0

        while i < len(nums):
            j = i
            while j + 1 < len(nums) and nums[j+1]==nums[j]+1 and missDict[nums[j+1]] == missDict[nums[i]]:
                j+=1
            merged.append((role, byNum[nums[i]].open, byNum[nums[j]].close, missDict[nums[i]]))

            i = j+1
    merged.sort(key=lambda m: (m[1], m[0]))

    return merged

def formatMissing(merged):
    lines = ["No valid schedule: Uncovered shift: "]
    for role, start, end, count in merged:
        extra = f" (short {count})" if count >1 else ""
        lines.append(f" {role} uncovered {formatTime(start)}-{formatTime(end)}{extra}")

    return "\n".join(lines)


def assign(block, role, employee):
    block.assignments.append((role, employee))
    employee.blocks.append(block)

def empTimeLeft(employee, block):
    hrLeft = employee.max_hours - employee.get_working_hours()
    return min(employee.close - block.open, hrLeft)

def greedySched(blocks, employeeList):
    for i, block in enumerate(blocks):
        previous = blocks[i-1].assignments if i > 0 else []

        for role in block.roles:
            eligibleEmps = getEligible(block, role, employeeList)
            cont = [emp for rol, emp in previous if rol == role and emp in eligibleEmps]

            if cont:
                assign(block, role, cont[0])
                continue

            longShiftEmp = [emp for emp in eligibleEmps if empTimeLeft(emp, block) >= MIN_SHIFT_HOURS]

            emplPool = longShiftEmp if longShiftEmp else eligibleEmps

            if not emplPool:
                return False

            pick = min(emplPool, key=lambda emp: emp.role_count())

            assign(block, role, pick)

    return True


def unassign(block, employee):
    block.assignments.pop()
    employee.blocks.pop()


def solve(index, slots, blocks, employeeList, state):
    # reached all slots
    if index == len(slots):
        return True
    state["steps"] += 1

    # reached max steps
    if state["steps"] > MAX_STEPS:
        return False

    block, role = slots[index]
    prev = blocks[block.blockNum-1].assignments if block.blockNum > 0 else []
    eligible = getEligible(block, role, employeeList)
    if not eligible:
        if index > state["deepest"]:
            state["deepest"] = index

        return False

    continuing = [emp for rol, emp in prev if rol == role]
    eligible = sorted(eligible, key=lambda empl: (empl not in continuing, empl.role_count()))


    # for each eligible employee try to assign and solve next slot, is fails, unassign and do next eligible
    for emp in eligible:
        assign(block, role, emp)
        if solve(index+1, slots, blocks, employeeList, state):
            return True
        unassign(block, emp)

    return False
    

def buildBacktracking(blocks, employeeList):
    slots = [(blk, rol) for blk in blocks for rol in blk.roles]
    state = {"steps": 0, "deepest": -1}

    # if schedule generated/found
    if(solve(0, slots, blocks, employeeList, state)):
        return True, None

    # if steps/loops reached max
    if state["steps"] > MAX_STEPS:
        return False, f"No valid schedule found after {MAX_STEPS} tries"

    badBlock, badRole = slots[state["deepest"]]

    return False, f"No valid schedule; {badRole} is not covered at {badBlock} (max hours)"

def buildSchedule(blocks, employeeList):
    mergedMissing = sweepUncovered(blocks, employeeList)

    if mergedMissing:
        return False, formatMissing(mergedMissing)

    if greedySched(blocks, employeeList):
        return True, None

    for blk in blocks:
        blk.assignments = []
    for emp in employeeList:
        emp.blocks = []

    return buildBacktracking(blocks, employeeList)

def coverPlan(employee, blockIndex, role, blocks):
    if role not in employee.roles:
        return None

    emplSpan = spanIndex(employee)

    if emplSpan is None:
        need = [blockIndex]
    elif blockIndex < emplSpan[0]:
        need = list(range(blockIndex, emplSpan[0]))
    elif blockIndex > emplSpan[1]:
        need = list(range(emplSpan[1]+1, blockIndex+1))
    else: 
        return None

    for i in need:
        if blocks[i].isWorking(employee) or not employee.is_available(blocks[i].open, blocks[i].close):
            return None

    if not employee.can_add_block(blocks[need[-1]].close - blocks[need[0]].open):
        return None

    return need


def tryMeal(blocks, order, employee, employeeList, covers, allowCover):
    for blockInd in order:
        block = blocks[blockInd]

        if not block.isWorking(employee) or any(blk is block for blk in employee.breaks):
            continue

        role = next(rol for rol, emp, in block.assignments if emp is employee)
        onDuty = sum (1 for rol, emp in block.assignments if rol == role)
        sub = None

        if onDuty -1 < block.roles.count(role):
            if not allowCover:
                continue
            options = []

            for emp in employeeList:
                if emp is employee:
                    continue

                plan = coverPlan(emp, blockInd, role, blocks)

                if plan:
                    options.append((emp, plan))

            if not options:
                continue

            sub, plan = min(options, key=lambda empOpt: (empOpt[0].role_count(), len(empOpt[1])))

            isNewShift = spanIndex(sub) is None

            for i in plan:
                assign(blocks[i], role, sub)

            covers.append((sub, role, isNewShift))

        block.assignments = [(rol,emp) for rol, emp in block.assignments if emp is not employee]

        employee.blocks.remove(block)
        employee.breaks.append(block)

        return True
    
    return False




def spansOf(employee):
    breakOpens = {blk.open: blk for blk in employee.breaks}
    shiftSpan = []
    for openT, closeT in shiftsOf(employee):
        if shiftSpan and shiftSpan[-1][1] in breakOpens and abs(openT - (shiftSpan[-1][1] + breakOpens[shiftSpan[-1][1]].size)) < 1e-9:
            shiftSpan[-1][1] = closeT
        else:
            shiftSpan.append([openT, closeT])

    return shiftSpan

def mealsFor(blocks, emp, employeeList, covers):
    for startT, endT in spansOf(emp):
        length = endT - startT
        waivedBreaks = [waive for waive in emp.waived if waive.endswith(f"({formatTime(startT)}-{formatTime(endT)})")]

        def breakBlocks():
            return sorted([blk for blk in emp.breaks if startT <= blk.open < endT], key=lambda blk: blk.open)

        for n in range(mealsRequired(length)):
            while sum(1 for blk in breakBlocks() if blk.open < startT + MEAL_DEADLINES[n]) <= n:
                if any(waive.startswith(f"meal {n+1} ") for waive in waivedBreaks):
                    break

                have = breakBlocks()
                target = startT + MEAL_TARGETS[n]
                deadline = startT + MEAL_DEADLINES[n]

                lo = startT + 1 if n==0 or len(have) < n else have[n-1].close + 2

                inRange = [i for i, bl in enumerate(blocks) if bl.close < endT and bl.open >= lo]

                primary = [i for i in inRange if target <= blocks[i].open < deadline]

                earlier = sorted([i for i in inRange if blocks[i].open < target], key=lambda i: -blocks[i].open)

                order = primary + earlier

                if (tryMeal(blocks, order, emp, employeeList, covers, False) or tryMeal(blocks, order, emp, employeeList, covers, True)):
                    continue

                if canWaiveMeal(n, length, len(have)):
                    waive = f"meal {n + 1} ({formatTime(startT)}-{formatTime(endT)})"
                    emp.waived.append(waive)
                    waivedBreaks.append(waive)
                    break

                return False, (f"No valid schedule. Cannot cover meal break {n + 1} for {emp.name} ({formatTime(startT)}-{formatTime(endT)})")

    return True, None
        

def placeBreaks(blocks, employeeList):
    for _ in range(8):
        covers = []
        for employee in employeeList:
            breakAdded, message = mealsFor(blocks, employee, employeeList, covers)

            if not breakAdded:
                return False, message

        if not covers:
            return True, None

        for empSub, role, newCov in covers:
            if not newCov:
                continue

            while empSub.get_working_hours() < MIN_SHIFT_HOURS:
                highInd = spanIndex(empSub)[1]
                if highInd + 1 >= len(blocks) or empSub not in getEligible(blocks[highInd +1], role, employeeList):
                    break
                assign(blocks[highInd +1], role, empSub)

    return False, "No valid schedule. Break placement did not settle."

def checkBreaks(employeeList):
    problems = []

    for employee in employeeList:
        if len(spansOf(employee)) > 1:
            pieces = ", ".join(f"{formatTime(openT)}-{formatTime(closeT)}" for openT, closeT in spansOf(employee))
            problems.append(f"{employee.name} has more than one shift: {pieces}")

        for openT, closeT in spansOf(employee):
            length = closeT - openT

            labelStr = f"{employee.name} {formatTime(openT)}-{formatTime(closeT)}"
            breaks = sorted(blk.open for blk in employee.breaks if openT <= blk.open < closeT)

            for n in range (mealsRequired(length)):
                onTime = sum(1 for brk in breaks if brk < openT + MEAL_DEADLINES[n])
                if onTime <= n and not canWaiveMeal(n, length, len(breaks)):
                    problems.append(f"{labelStr}: meal {n+1} missing or starts too late (can't be waived)")


    return problems

def checkCoverage(blocks):
    for block in blocks:
        for role in set(block.roles):
            have = sum (1 for rol, emp in block.assignments if rol == role)
            if have < block.roles.count(role):
                return False

    return True

def shiftsOf(employee):
    byBlockNum = {block.blockNum: block for block in employee.blocks}
    bNums = sorted(byBlockNum)

    shift = []
    i = 0
    while i < len(bNums):
        j = i

        while j + 1 < len(bNums) and bNums[j+1] == bNums[j]+1:
            j+=1

        shift.append((byBlockNum[bNums[i]].open, byBlockNum[bNums[j]].close))
        i = j+1

    return shift


def printSchedule(blocks, employeeList):
    for employee in employeeList:
        if employee.blocks:
            shiftStr = ", ".join(f"{formatTime(startT)}-{formatTime(endT)}" for startT,endT in shiftsOf(employee))
            breakStr = [f"30-min meal {formatTime(blk.open)}-{formatTime(blk.close)}" for blk in sorted(employee.breaks, key=lambda b: b.open)]
            breakStr += [f"{waive} WAIVED" for waive in employee.waived]
            tailStr = (" ["+"; ".join(breakStr)+"]") if breakStr else ""
            print(f" {employee.name} [{'/'.join(employee.roles)}]: {shiftStr} = {employee.get_working_hours()}h{tailStr}")

def resetEmployees(employeeList):
    for employee in employeeList:
        employee.blocks = []
        employee.breaks = []
        employee.waived = []

    
def run(openTime, closeTime, blockSize, roleList, employees):
    resetEmployees(employees)
    blocks = splitBlocks(openTime, closeTime, blockSize)
    addRoles(blocks, roleList)

    schedBuilt, message = buildSchedule(blocks, employees)

    if schedBuilt:
        schedBuilt, message = placeBreaks(blocks, employees)

    if schedBuilt:
        problems = checkBreaks(employees)
        print("Valid schedule" + ("" if checkCoverage(blocks) else "~~ COVERAGE CHECK FAILED"))
        printSchedule(blocks, employees)

        for prob in problems:
            print(" !! BREAK CHECK: ", prob)
    else:
        print(message)

    return schedBuilt

