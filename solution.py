import sys
import math

chromosome = [
    {
        "feature": "days",
        "op": "<",
        "value": 0.0,
        "action": "add_per_day",
        "amount": 105.65060124410864,
        "enabled": false
    },
    {
        "feature": "miles",
        "op": ">",
        "value": 58.87760775631369,
        "action": "add_per_mile",
        "amount": 0.7253462550062706,
        "enabled": true
    },
    {
        "feature": "miles",
        "op": "<",
        "value": 118.78636288959345,
        "action": "add_per_mile",
        "amount": 1.4456783704886165,
        "enabled": true
    },
    {
        "feature": "receipts",
        "op": ">",
        "value": 0.0,
        "action": "mult_feature",
        "amount": 0.5302075004029059,
        "enabled": true
    },
    {
        "feature": "daily_spend",
        "op": ">",
        "value": 161.33016516743518,
        "action": "add_amount",
        "amount": -194.26178841668238,
        "enabled": true
    },
    {
        "feature": "miles_per_day",
        "op": ">",
        "value": 552.8295453182443,
        "action": "add_amount",
        "amount": -289.90020074032685,
        "enabled": false
    },
    {
        "feature": "days",
        "op": "==",
        "value": 4.260070235137968,
        "action": "add_amount",
        "amount": 67.44080644648344,
        "enabled": true
    },
    {
        "feature": "miles_per_day",
        "op": "<",
        "value": 212.2825211389645,
        "action": "add_amount",
        "amount": 432.824307981654,
        "enabled": true
    },
    {
        "feature": "miles_per_day",
        "op": "<",
        "value": 37.928408116630685,
        "action": "add_amount",
        "amount": -140.01606471862993,
        "enabled": false
    }
]

# model_rule_engine.py
import math

def calculate_reimbursement(days, miles, receipts, chromosome):
    """
    This function acts as a dynamic rule engine. It takes a 'chromosome'
    (a list of rule genes) and applies them sequentially to calculate the reimbursement.
    """
    if days <= 0: return 0.0

    # --- Base Values & Derived Metrics ---
    # The chromosome itself will define how these are used.
    reimbursement = 0.0
    daily_spend = receipts / days if days > 0 else 0
    miles_per_day = miles / days if days > 0 else 0

    # --- The Rule Engine ---
    # The chromosome is a list of rules. We process them in order.
    for gene in chromosome:
        if not gene.get('enabled', True):
            continue # This rule has been mutated to be "off"

        # Check if the condition for this rule is met
        value_to_check = {
            'days': days, 'miles': miles, 'receipts': receipts,
            'daily_spend': daily_spend, 'miles_per_day': miles_per_day
        }[gene['feature']]

        op = gene['op']
        condition_met = False
        if op == '>': condition_met = value_to_check > gene['value']
        elif op == '<': condition_met = value_to_check < gene['value']
        elif op == '==': condition_met = value_to_check == gene['value']

        if condition_met:
            # Apply the action
            action = gene['action']
            if action == 'set_base': reimbursement = gene['amount']
            elif action == 'add_amount': reimbursement += gene['amount']
            elif action == 'mult_feature': reimbursement += value_to_check * gene['amount']
            elif action == 'add_per_day': reimbursement += days * gene['amount']
            elif action == 'add_per_mile': reimbursement += miles * gene['amount']

    return round(max(0, reimbursement), 2)
if __name__ == "__main__":
    if len(sys.argv) != 4: sys.exit(1)
    try:
        result = calculate_reimbursement(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), chromosome)
        print(f"{result:.2f}")
    except Exception: print(0.0)
