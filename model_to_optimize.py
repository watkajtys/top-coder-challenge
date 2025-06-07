# model_to_optimize.py (Version 5.1 - with Trip Profile)
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount, params):
    if trip_duration_days <= 0: return 0.0
    trip_duration_days = int(trip_duration_days)
    miles_traveled = float(miles_traveled)
    total_receipts_amount = float(total_receipts_amount)

    daily_spend = total_receipts_amount / trip_duration_days if trip_duration_days > 0 else 0
    miles_per_day = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0

    per_diem_total = params['base_per_diem_rate'] * trip_duration_days

    mileage_total = 0
    if trip_duration_days < params['long_trip_days_cutoff']:
        cutoff = params['short_mileage_tier_cutoff']
        if miles_traveled <= cutoff:
            mileage_total = miles_traveled * params['short_mileage_rate_t1']
        else:
            mileage_total = (cutoff * params['short_mileage_rate_t1']) + ((miles_traveled - cutoff) * params['short_mileage_rate_t2'])
    else:
        mileage_total = miles_traveled * params['long_mileage_rate']

    receipt_reimbursement = 0
    if 0 < total_receipts_amount < params['small_receipt_penalty_threshold']:
        receipt_reimbursement = params['small_receipt_penalty_amount']
    else:
        allowance_multiplier = params['receipt_mult_default']
        if daily_spend < params['receipt_generous_spend_threshold']:
            allowance_multiplier = params['receipt_mult_generous']
        receipt_reimbursement = total_receipts_amount * allowance_multiplier

    adjustment = 0
    # Simulate a "Sales Trip Profile" with more aggressive bonuses
    if params['trip_profile'] == 1:
        if trip_duration_days < params['long_trip_days_cutoff'] and miles_per_day > params['efficiency_bonus_min_miles_per_day']:
            adjustment += (miles_per_day - params['efficiency_bonus_min_miles_per_day']) * params['efficiency_bonus_rate']

    if trip_duration_days >= params['long_trip_days_cutoff'] and daily_spend > params['long_trip_spend_penalty_threshold']:
        adjustment -= (daily_spend - params['long_trip_spend_penalty_threshold']) * params['long_trip_spend_penalty_rate']

    if trip_duration_days == 5:
        adjustment += params['bonus_5_day_amount']

    if 8 <= trip_duration_days <= 10 and daily_spend <= params['long_trip_spend_penalty_threshold']:
        adjustment += params['bonus_8_10_day_amount']

    receipt_cents = int(round(total_receipts_amount * 100)) % 100
    if receipt_cents in [49, 99]:
        adjustment += params['bonus_rounding_bug_amount']

    final_amount = per_diem_total + mileage_total + receipt_reimbursement + adjustment
    return round(max(0, final_amount), 2)