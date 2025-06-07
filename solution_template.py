# solution_template.py (Path-Based Model)

import math
import sys

# This new structure uses path-specific functions for clarity and better tuning.
def _calculate_long_haul(days, miles, receipts, params):
    # Kevin's "vacation penalty" path
    daily_spend = receipts / days if days > 0 else 0

    per_diem = days * params['long_per_diem_rate']
    mileage = miles * params['long_mileage_rate']

    receipt_mult = params['long_receipt_mult_normal']
    if daily_spend > params['long_receipt_spend_penalty_threshold']:
        receipt_mult = params['long_receipt_mult_penalty']

    receipts_total = receipts * receipt_mult
    return per_diem + mileage + receipts_total

def _calculate_standard_trip(days, miles, receipts, params):
    # Lisa's "sweet spot" and tiered model path
    per_diem = days * params['std_per_diem_rate']

    mileage = 0
    if miles > 0:
        if miles <= params['std_mileage_tier_1_cutoff']:
            mileage = miles * params['std_mileage_rate_tier_1']
        else:
            mileage = (params['std_mileage_tier_1_cutoff'] * params['std_mileage_rate_tier_1']) + \
                      ((miles - params['std_mileage_tier_1_cutoff']) * params['std_mileage_rate_tier_2'])

    receipts_total = receipts * params['std_receipt_mult']

    bonus = 0
    if days == params['std_bonus_5_day_duration']:
        bonus += params['std_bonus_5_day_amount']

    return per_diem + mileage + receipts_total + bonus

def _calculate_local_trip(days, miles, receipts, params):
    # The default path for short, common trips
    per_diem = days * params['local_per_diem_rate']
    mileage = miles * params['local_mileage_rate']

    receipts_total = 0
    if 0 < receipts < params['local_receipt_penalty_threshold']:
        receipts_total = params['local_receipt_penalty_amount']
    else:
        receipts_total = receipts * params['local_receipt_mult']

    return per_diem + mileage + receipts_total

def _calculate_hyper_efficient(days, miles, receipts, params):
    # A special punitive path for trips with extreme miles/day ratios
    # This directly targets the huge error cases.
    per_diem = days * params['hyper_per_diem_rate']
    mileage = miles * params['hyper_mileage_rate'] # Very low rate
    receipts_total = receipts * params['hyper_receipt_mult'] # Very low multiplier

    return per_diem + mileage + receipts_total

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount, params):
    if trip_duration_days <= 0:
        return 0.0

    miles_traveled = float(miles_traveled)
    total_receipts_amount = float(total_receipts_amount)

    miles_per_day = miles_traveled / trip_duration_days

    # --- TOP-LEVEL CLASSIFIER ---
    # This is the most critical part of the new model. It routes the trip
    # to the correct calculation path based on its characteristics.

    # Path 1: Hyper-Efficient (Punitive) - Fixes the biggest error cases
    if trip_duration_days <= 3 and miles_per_day > 400:
        reimbursement = _calculate_hyper_efficient(trip_duration_days, miles_traveled, total_receipts_amount, params)
    # Path 2: Long Haul (>= 8 days)
    elif trip_duration_days >= 8:
        reimbursement = _calculate_long_haul(trip_duration_days, miles_traveled, total_receipts_amount, params)
    # Path 3: Standard Business Trip (4-7 days)
    elif 4 <= trip_duration_days <= 7:
        reimbursement = _calculate_standard_trip(trip_duration_days, miles_traveled, total_receipts_amount, params)
    # Path 4: Local Trip (1-3 days) - Default Case
    else:
        reimbursement = _calculate_local_trip(trip_duration_days, miles_traveled, total_receipts_amount, params)

    # A single, global adjustment can still be useful
    final_reimbursement = reimbursement + params['global_offset']

    return round(max(0, final_reimbursement), 2)


# This block allows the script to be run directly if needed, using a default set of parameters.
if __name__ == "__main__":
    # --- DEFAULT PARAMETERS (This part will be overwritten by the trainer) ---
    final_params = {
        'local_per_diem_rate': 100.0, 'local_mileage_rate': 0.7, 'local_receipt_mult': 0.7,
        'local_receipt_penalty_threshold': 20.0, 'local_receipt_penalty_amount': -15.0,
        'std_per_diem_rate': 120.0, 'std_mileage_rate_tier_1': 0.58, 'std_mileage_rate_tier_2': 0.45,
        'std_mileage_tier_1_cutoff': 100, 'std_receipt_mult': 0.85, 'std_bonus_5_day_duration': 5,
        'std_bonus_5_day_amount': 55.0,
        'long_per_diem_rate': 150.0, 'long_mileage_rate': 0.55, 'long_receipt_mult_normal': 0.8,
        'long_receipt_spend_penalty_threshold': 90.0, 'long_receipt_mult_penalty': 0.3,
        'hyper_per_diem_rate': 50.0, 'hyper_mileage_rate': 0.25, 'hyper_receipt_mult': 0.15,
        'global_offset': 0.0
    }

    if len(sys.argv) != 4:
        print("Usage: python solution_template.py <days> <miles> <receipts>")
        sys.exit(1)

    duration = int(sys.argv[1])
    miles = float(sys.argv[2])
    receipts = float(sys.argv[3])

    result = calculate_reimbursement(duration, miles, receipts, final_params)
    print(result)