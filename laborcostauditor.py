from datetime import datetime

# --- CUSTOM ERROR DEFINITION ---
# This allows us to create a specific error message if sales are missing/zero later.
class NetSalesError(Exception):
    pass

# --- INPUT HELPER: NUMBERS ---
# This function handles all number entries (hours, breaks).
# It prevents the program from crashing if a user types a letter instead of a number.
def get_float_input(prompt, allow_zero=True):
    while True:
        user_input = input(prompt).strip()
        
        # If the user just hits ENTER, we treat it as 0.0
        if user_input == "":
            val = 0.0
        else:
            try:
                val = float(user_input)
            except ValueError:
                # If they type something like "eight", tell them to use numbers
                print("    Invalid Input: Please enter a number.")
                continue
        
        # Validation: Reject 0 for 'Total Hours Worked' but allow it for 'Break Time'
        if not allow_zero and val <= 0:
            print("    Invalid: Hours worked must be greater than 0.")
            continue
        # Standard check to ensure no negative numbers are entered
        elif val < 0:
            print("    Invalid: Value cannot be negative.")
            continue
            
        return round(val, 2)

# --- INPUT HELPER: YES/NO ---
# This function ensures the user only types 'y' or 'n', preventing typos from breaking the flow.
def get_yn_input(prompt):
    while True:
        user_input = input(prompt).lower().strip()
        if user_input in ['y', 'n']:
            return user_input
        print("    ⚠️ Invalid Input: Please type 'y' or 'n'.")

def main():
    # --- DATE & TIME HEADER ---
    # We use a try/except here so if the computer's clock has an issue, the script doesn't crash.
    try:
        now = datetime.now()
        day = now.day
        # This adds the correct suffix (1st, 2nd, 3rd, 4th) to the day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        formatted_date = now.strftime(f"%A, %B {day}{suffix}, at %I:%M %p")
        print(f"\n--- Labor Report for {formatted_date} ---")
        print("💡 Tip: Just press ENTER if the count is 0.")
    except Exception:
        # Emergency fallback name for the report
        formatted_date = "Current Shift"
        print("\n--- End of Shift Labor Report ---")

    # Visual separator for the terminal
    print(f"\n{'='*65}")
    print(f"CALIFORNIA LABOR AUDITOR | {formatted_date}")
    print(f"{'='*65}")

    # Set the static sales amount for the audit
    net_sales = 7500.00

    # --- STAFF DATABASE ---
    # List of employees with their department and hourly pay rate.
    staff = [
        {"name": "Ever Flores", "dept": "BOH", "hourly_rate": 22.00},
        {"name": "Edward Ramirez", "dept": "BOH", "hourly_rate": 22.00},
        {"name": "Bai Gong", "dept": "BOH", "hourly_rate": 21.00},
        {"name": "Jose Espinosa", "dept": "BOH", "hourly_rate": 23.00},
        {"name": "Jorge Verrera", "dept": "BOH", "hourly_rate": 25.00},
        {"name": "Maureen Manilla", "dept": "FOH", "hourly_rate": 18.00},
        {"name": "Cindy Quintilla", "dept": "FOH", "hourly_rate": 18.00},
        {"name": "Samantha Adler", "dept": "FOH", "hourly_rate": 18.00},
        {"name": "Malina Manni", "dept": "FOH", "hourly_rate": 18.00},
        {"name": "Nichole Crawford", "dept": "FOH", "hourly_rate": 18.00}
    ]

    # --- PROCESSING LOOP ---
    # We go through the staff list one by one to collect their shift data.
    for person in staff:
        print(f"\nProcessing: {person['name']} ({person['dept']})")
        
        # 1. Collect Total Hours (Safety check for shifts over 14 hours)
        while True:
            # We pass allow_zero=False because an employee being processed must have worked.
            raw_hours = get_float_input(f"  Enter total hours worked: ", allow_zero=False)
            if raw_hours > 14.00:
                print(f"    🚩 SANITY CHECK: {raw_hours} hours seems high.")
                if get_yn_input("    Is this a mistake? (y=re-enter/n=confirm): ") == 'y':
                    continue
            break
        
        # 2. Collect Break Data & Check for California Compliance
        break_time = 0.0
        is_violation = False
        if get_yn_input(f"  Did they take a meal break? (y/n): ") == 'y':
            while True:
                break_time = get_float_input(f"  How long was the break? (e.g., 0.50): ")
                # Check: Break can't be longer than the whole shift
                if break_time >= raw_hours:
                    print(f"    ❌ Error: Break ({break_time}) cannot be longer than or equal to total shift ({raw_hours}).")
                # Check: A 1.5 hour break is usually a mistake/split shift
                elif break_time > 1.30:
                    print(f"    ❌ Error: Break ({break_time}) exceeds the maximum allowed limit of 1.30 hours.")
                else:
                    break
            
            # Violation: Shift > 6 hours requires at least a 30-minute (0.50) break
            if raw_hours > 6.00 and break_time < 0.50:
                is_violation = True
                print(f"  ⚠️ Short Break Violation: {break_time} < 0.50. Penalty triggered.")
        
        # Violation: No break taken on a shift longer than 6 hours
        elif raw_hours > 6.00:
            is_violation = True
            print("  ⚠️ Meal Violation: No break on shift > 6hrs. Penalty triggered.")

        # 3. Calculate Pay (Regular, Overtime, and Penalties)
        # Net pay hours = Total hours minus the unpaid break
        pay_hours = raw_hours - break_time
        
        # Overtime Alert: California daily OT starts after 8 net hours
        if pay_hours > 8.00:
            print(f"  🚨 ALERT: Overtime Detected ({pay_hours:.2f} net hours).")

        # Math for Overtime vs Regular time
        over_time = max(0, pay_hours - 8.00)
        reg_hours = min(pay_hours, 8.00)
        
        # Penalty Pay: In California, a violation adds 1 hour of pay at the regular rate
        penalty_pay = person['hourly_rate'] if is_violation else 0.0
        
        # Final Total: (Reg * Rate) + (OT * Rate * 1.5) + Penalty Hour
        total_pay = (reg_hours * person['hourly_rate']) + (over_time * person['hourly_rate'] * 1.5) + penalty_pay

        # Store all the calculated data back into the person's dictionary
        person.update({
            "hours_worked": pay_hours,
            "over_time": over_time,
            "is_violation": is_violation,
            "total_pay": total_pay,
            "penalty_pay": penalty_pay
        })

    # --- STEP 2: FINAL REPORT GENERATION ---
    # Send all collected data to the reporting function.
    generate_full_reports(staff, net_sales, formatted_date)

def generate_full_reports(staff, net_sales, date_str):
    # Initialize counters for the dashboard
    grand_totals = {"BOH": 0.0, "FOH": 0.0, "hours": 0.0, "ot_cost": 0.0, "penalty_cost": 0.0}
    
    # --- DEPARTMENT TABLES ---
    # Separates staff into BOH (Kitchen) and FOH (Service) for clear viewing
    print(f"\n{'='*65}\n{'OFFICIAL LABOR AUDIT':^65}\n{'='*65}")

    for dept in ["BOH", "FOH"]:
        print(f"\n--- {dept} STAFF LIST ---")
        print(f"{'Name':<18} | {'Wage':<6} | {'Hours':<6} | {'Total Pay':>10}")
        print("-" * 55)
        
        current_dept_total = 0.0
        for p in staff:
            if p['dept'] == dept:
                # Print the individual line for each employee
                print(f"{p['name']:<18} | ${p['hourly_rate']:<5.2f} | {p['hours_worked']:<6.2f} | ${p['total_pay']:>9.2f}")
                
                # Add their numbers to the running totals
                current_dept_total += p['total_pay']
                grand_totals["hours"] += p['hours_worked']
                grand_totals["ot_cost"] += (p['over_time'] * p['hourly_rate'] * 1.5)
                grand_totals["penalty_cost"] += p['penalty_pay']
        
        # Calculate Labor % for just this department
        grand_totals[dept] = current_dept_total
        pct = (current_dept_total / net_sales) * 100
        print(f"\nTotal {dept} Cost: ${current_dept_total:,.2f} ({pct:.2f}% of Sales)")
        
        # Budget Check: BOH Target < 15%, FOH Target < 5%
        budget = 15 if dept == "BOH" else 5
        if pct > budget: 
            print(f"❌ ALERT: {dept} OVER BUDGET (Limit: {budget}%)")

    # --- EXECUTIVE DASHBOARD ---
    # High-level summary for the owner or general manager
    total_wages = grand_totals["BOH"] + grand_totals["FOH"]
    labor_pct = (total_wages / net_sales) * 100
    
    # SPLH = Sales Per Labor Hour (Measures productivity)
    splh = net_sales / grand_totals["hours"] if grand_totals["hours"] > 0 else 0

    print(f"\n{'='*65}\n{'EXECUTIVE MANAGER DASHBOARD':^65}\n{date_str:^65}\n{'='*65}")
    print(f"{'Metric':<25} | {'Value':<12} | {'Status'}")
    print("-" * 65)
    
    # Total Labor % Status
    l_status = '✅ OK' if labor_pct <= 20 else '❌ OVER'
    print(f"{'Overall Labor %':<25} | {labor_pct:>11.2f}% | {l_status}")
    
    # Productivity Status
    s_status = '✅ Great' if 65 <= splh <= 85 else '📢 Alert'
    print(f"{'Productivity (SPLH)':<25} | ${splh:>10.2f} | {s_status}")
    
    # --- ACTION ITEMS ---
    # Provides specific steps to fix any issues found in the audit
    print("-" * 65 + "\nACTION ITEMS:")
    
    # Goal Math: If labor is high, tell the manager how many more sales were needed to hit 20%
    if labor_pct > 20:
        goal_gap = (total_wages / 0.20) - net_sales
        print(f"  👉 Labor high. Need ${goal_gap:,.2f} more in sales to hit 20% goal.")
    
    # List all employees who had a compliance violation
    violators = [p['name'] for p in staff if p['is_violation']]
    if violators: 
        print(f"  👉 Compliance: Review breaks with {', '.join(violators)}.")
    
    # Show the total cost of legal penalties today
    print(f"  👉 Total Penalty Costs: ${grand_totals['penalty_cost']:,.2f}")
    print(f"{'='*65}\n")

# Standard Python boilerplate to run the program
if __name__ == "__main__":
    main()
