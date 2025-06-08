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