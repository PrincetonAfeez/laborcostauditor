#Project: The "Smart" Labor Cost Auditor
#Focus: Use modules to grab data from inventorymanager.py

import sys  # Library for system exits and error handling
from datetime import datetime  # Library for generating shift timestamps
# Import your custom modules
from validator import get_int, get_float  # Standardized input validation
import inventorymanager as inv_mgr  # Link to the inventory and sales data engine

# ==========================================
# PHASE 1: THE SETUP (THE "BRAIN")
# ==========================================

def main():
    """Main execution point for the Labor Auditor."""
    # --- DATE & TIME HEADER ---
    try:
        now = datetime.now()  # Grab the current system time
        day = now.day  # Extract the day of the month
        # Determine the correct ordinal suffix for the date (st, nd, rd, th)
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        formatted_date = now.strftime(f"%A, %B {day}{suffix}, at %I:%M %p")  # Format: Monday, March 15th...
        print(f"\n--- Labor Report for {formatted_date} ---")
    except Exception:
        formatted_date = "Current Shift"  # Fallback string if datetime fails
        print("\n--- End of Shift Labor Report ---")

    # Visual UI header for the terminal
    print(f"\n{'='*65}")
    print(f"CALIFORNIA LABOR AUDITOR | {formatted_date}")
    print(f"{'='*65}")

    # 2. FETCH SHARED DATA (The Data Bridge)
    print("🚀 Initializing Shift Audit: Syncing with Inventory Sales...")
    
    # MODIFIED: inventorymanager.py must now return its calculated revenue.
    # We wrap this in a try/except to catch any module-level crashes.
    try:
        # We assume run_inventory_audit() has been updated to 'return total_net'
        net_sales = inv_mgr.run_inventory_audit()
    except Exception as e:
        print(f"⚠️  Sync Warning: Could not automate sales data. {e}")
        net_sales = None # Set to None to trigger the manual fallback below

    # Safety check: If the sync returned nothing or zero, we trigger a manual override
    if net_sales is None or net_sales <= 0:
        print("\n⚠️  NOTICE: No automated sales data found.")
        # Feature 1 & 4: Loop until valid manual sales are entered
        confirm = input("Would you like to enter sales manually? (y/n): ").lower()
        if confirm == 'y':
            net_sales = get_float("  Enter total net sales for the shift: $", min_val=0.01)
        else:
            print("❌ Audit aborted: Cannot calculate labor without sales revenue.")
            sys.exit()

    print(f"\n✅ SALES SYNC COMPLETE: ${net_sales:,.2f} loaded for labor analysis.")
    
    # --- STAFF DATABASE ---
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

    # ==========================================
    # PHASE 2: DATA ENTRY LOOP (STAFF COLLECTION)
    # ==========================================
    
    for person in staff:  # Iterate through the employee roster
        print(f"\nProcessing: {person['name']} ({person['dept']})")
        
        # 1. Collect Total Hours (Feature 3: Fat Finger Guardrail)
        while True:
            raw_hours = get_float(f"  Enter total hours worked: ", min_val=0)
            if raw_hours > 14.00:  # California safety check for extreme shifts
                print(f"    🚩 SANITY CHECK: {raw_hours} hours seems high.")
                if input("    Is this correct? (y/n): ").lower().strip() != 'y':
                    continue
            break
        
        # 2. Collect Break Data & Check for California Compliance
        break_time = 0.0
        is_violation = False
        took_break = input(f"  Did they take a meal break? (y/n): ").lower().strip()
        
        if took_break == 'y':
            while True:
                break_time = get_float(f"  How long was the break? (e.g., 0.50): ", min_val=0)
                if break_time >= raw_hours or break_time > 1.30: # Max break limit 1.5hrs
                    print(f"    ❌ Error: Invalid break duration.")
                else:
                    break
            
            # Violation: Shift > 6 hours requires at least a 30-minute (0.50) break
            if raw_hours > 6.00 and break_time < 0.50:
                is_violation = True
        elif raw_hours > 6.00:
            is_violation = True  # Penalty if no break taken on long shift

        # 3. Calculate Pay (Regular, Overtime, and Penalties)
        pay_hours = raw_hours - break_time  # Unpaid meal break subtraction
        over_time = max(0, pay_hours - 8.00)  # Daily OT starts after 8 hours in CA
        reg_hours = min(pay_hours, 8.00)  # Regular pay capped at 8 hours
        
        # Penalty Pay: 1 hour of extra pay for meal violations
        penalty_pay = person['hourly_rate'] if is_violation else 0.0
        
        # Math for total payroll cost per person
        total_pay = (reg_hours * person['hourly_rate']) + (over_time * person['hourly_rate'] * 1.5) + penalty_pay

        # Update the person dictionary with the shift results
        person.update({
            "hours_worked": pay_hours,
            "over_time": over_time,
            "is_violation": is_violation,
            "total_pay": total_pay,
            "penalty_pay": penalty_pay
        })

    # ==========================================
    # PHASE 3: THE REPORTS (THE "OUTPUT")
    # ==========================================
    generate_full_reports(staff, net_sales, formatted_date)

def generate_full_reports(staff, net_sales, formatted_date):
    """Calculates totals and displays the final labor analysis tables."""
    total_foh_wages = 0.0
    total_boh_wages = 0.0
    total_hours = 0.0
    total_ot_costs = 0.0
    total_penalty_costs = 0.0

    print(f"\n{'='*65}\n{'OFFICIAL LABOR AUDIT':^65}\n{'='*65}")

    for dept in ["BOH", "FOH"]: # Separate display for Kitchen and Floor
        print(f"\n--- {dept} STAFF LIST ---")
        print(f"{'Name':<18} | {'Wage':<6} | {'Hours':<6} | {'Total Pay':>10}")
        print("-" * 55)
        
        for p in staff:
            if p['dept'] == dept:
                print(f"{p['name']:<18} | ${p['hourly_rate']:<5.2f} | {p['hours_worked']:<6.2f} | ${p['total_pay']:>9.2f}")
                total_hours += p['hours_worked']
                total_penalty_costs += p['penalty_pay']
                total_ot_costs += (p['over_time'] * p['hourly_rate'] * 0.5) # The OT premium
                
                if dept == "BOH": total_boh_wages += p['total_pay']
                else: total_foh_wages += p['total_pay']
        
        # Department labor percentage calculation
        dept_total = total_boh_wages if dept == "BOH" else total_foh_wages
        pct = (dept_total / net_sales) * 100 if net_sales > 0 else 0
        print(f"\nTotal {dept} Cost: ${dept_total:,.2f} ({pct:.2f}% of Sales)")

    # --- EXECUTIVE DASHBOARD ---
    total_wages = total_foh_wages + total_boh_wages
    labor_percentage = (total_wages / net_sales) * 100 if net_sales > 0 else 0
    splh = net_sales / total_hours if total_hours > 0 else 0
        
    print(f"\n{'='*65}\n{'EXECUTIVE MANAGER DASHBOARD':^65}\n{'='*65}")
    l_status = '✅ OK' if labor_percentage <= 20 else '❌ OVER'
    print(f"{'Overall Labor %':<25} | {labor_percentage:>11.2f}% | {l_status}")
    print(f"{'Productivity (SPLH)':<25} | ${splh:>10.2f} | {'📢 Alert' if splh < 65 else '✅ OK'}")

    # ACTION ITEMS
    print("-" * 65 + "\nACTION ITEMS:")
    if labor_percentage > 20:
        goal_gap = (total_wages / 0.20) - net_sales
        print(f"  👉 Labor high. Increase sales by ${goal_gap:,.2f} to hit 20% goal.")
    
    violators = [p['name'] for p in staff if p['is_violation']]
    if violators: print(f"  👉 Compliance: Review breaks with {', '.join(violators)}.")

if __name__ == "__main__":
    main()

