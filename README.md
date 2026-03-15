# laborcostauditor
Python Script that audits a shifts labor cost
Project: The "Smart" Labor Cost Auditor
Concept Focus: Floats, Conditionals, Loops, and Input Validation.
The Scenario: You need to audit a shift's labor.

The Task: 
Create a program that prompts the user to enter hours worked for each staff
then calculates their page while considering overtime and meal break violation

1. The Constraint: input validation
If the user enters a negative number or a word, 
the program must not crash; it should say "Invalid Input" and ask again.
*total_net_sales can't be 0
*all user input must be positive float execpt for meal_break which is y/n

2. The "Goal" Sales Calculator
Instead of just saying "Labor is too high," the program could calculate exactly how much more sales are needed to hit the target.
*The Math: If labor is at 25% and the goal is 20%, 
*Benefit: Gives the manager a sales target for the rest of the shift.
*Print the Labor Percentage (total_wages / total_net_sales)

3. Role-Based Labor Breakdown
A manager often needs to know who is costing the most. You could add a "Role" input (e.g., Kitchen, Front of House, BOH).
*The Logic: At the end, show:
*Establish baseline, BOH_baseline is 15% and FOH_baseline is 5%, now you can alert
*Benefit: If labor is higher than baseline, the manager knows whether to cut a server or a prep cook.

4. Overtime (OT) Detection
In California, hours over 8 in a shift (or 40 in a week) are paid at 1.5x
*The Logic: Inside your loop
    -if hours_worked > 8, the program automatically calculates the extra cost.
    -print early warning if user_input is over 8 hours

5. Break Violation Premiun
if a manager fails to provide a compliant meal or rest break, they owe the employee one additional hour of pay at the employee's regular rate of compensation.
*Ask if the staff took a 30 minutes meal break,
    -if yes, deduct 30 minutes from the staff's pay
    -if not, add an extra hour to the staff's pay and alert, staff will receive an extra hour's pay

6. Reports:
a. Dept Breakdown BOH List, then FOH list (granular)
    -print staff's name, dept, hourly_wage, hours_worked, meal_break, overtime and total pay for each staff
    -print total_boh_labor and boh_labor_percentage, if boh_baseline > 15% alert boh is over budget
    -print total_foh_labor and foh_labor_percentage, if foh_baseline > 5% alert boh is over budget

b. Compliance
    -print overtime costs
    -print mealbreak violation costs

c. Goal Tracker
    -print total_net_sales
    -print total_labor cost
    -print total_labor_hours
    -print labor_percentage
    -print productivity (SPLH = total_net sales / total_hours_worked), if high SPLH (>$85), you were under staff, if low SPLH(<$65), you were overstaff, otherwise staffing levels are great


Pseudocode

Phase 1: The Setup (Before the Loop)
*Initialize Variables: Set total_foh_wages, total_boh_wages, total_hours, total_ot_costs, and total_penalty_costs to 0.0.
*Prepare Storage: Create two empty lists: foh_staff_list and boh_staff_list.
*Get Sales (Input Validation):
    -Start a while True loop.
    -try to get float(input("Total Sales: ")).
    -if sales is < 0, print "Invalid Input" and continue.
    -except ValueError, print "Invalid Input" and continue.
    -break once valid.

Phase 2: The Data Entry Loop (Staff Collection)
START WHILE LOOP:
1. Meal Break Check: Ask "Did they take a 30m meal break? (y/n)".
*IF "y": hours = hours - 0.5.
*IF "n": penalty_pay = 1 * wage. Add this to total_penalty_costs. Print "Violation Alert: Adding 1hr pay."
5. Calculate Individual Pay:
*IF hours > 8:
    -regular_pay = 8 * wage
    -ot_pay = (hours - 8) * (wage * 1.5)
    -Add the "extra half-time" amount (hours - 8) * (wage * 0.5) to total_ot_costs.
*ELSE: regular_pay = hours * wage, ot_pay = 0.
*total_individual_pay = regular_pay + ot_pay + penalty_pay.
6. Store Data: Save all this info into a dictionary and .append() it to either the foh_staff_list or boh_staff_list.

Phase 3: The Reports (After the Loop)
A. Dept Breakdown
*Loop through boh_staff_list. Print name, wage, hours, and pay for each.
*Repeat for foh_staff_list.
*Calculate BOH and FOH % of sales.
    -IF BOH % > 15%: Print "BOH OVER BUDGET."
    -IF FOH % > 5%: Print "FOH OVER BUDGET."

B. Compliance Audit
*Print total_ot_costs and total_penalty_costs.

C. Goal Tracker & Productivity
*Labor %: (Total BOH + Total FOH) / Sales.
*IF Labor % > 20%:
    -Print "WARNING: Cut Staff."
    -Target Sales Math: (Total Wages / 0.20) - Current Sales. Print this as the "Goal."
*SPLH (Productivity): Sales / Total Hours.
    -IF > $85: "Understaffed."
    -IF < $65: "Overstaffed."
    -ELSE: "Staffing levels are great."
