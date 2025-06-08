# model_template.py (Purpose-Driven Model)
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount, params):
    if trip_duration_days <= 0: return 0.0
    trip_duration_days = int(trip_duration_days)
    miles_traveled = float(miles_traveled)
    total_receipts_amount = float(total_receipts_amount)

    miles_per_day = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0

    # ==========================================================================
    # 1. TOP-LEVEL CLASSIFIER: Determine Trip Profile
    # ==========================================================================
    trip_profile = 'STANDARD' # Default
    if miles_per_day > params['road_warrior_min_miles_per_day']:
        trip_profile = 'ROAD_WARRIOR'
    elif miles_per_day < params['on_site_max_miles_per_day']:
        trip_profile = 'ON_SITE'

    # Override for punitive edge cases
    if (trip_duration_days <= 2 and miles_per_day > 450) or (trip_duration_days >= 14):
        trip_profile = 'PUNITIVE'

    # ==========================================================================
    # 2. PATH-SPECIFIC CALCULATIONS
    # ==========================================================================
    reimbursement = 0

    if trip_profile == 'ROAD_WARRIOR':
        # Generous mileage, standard per-diem, stricter receipt scrutiny.
        per_diem = trip_duration_days * params['rw_per_diem_rate']
        # Highly rewarding mileage for the "hustle"
        mileage = miles_traveled * params['rw_mileage_rate']
        receipts = total_receipts_amount * params['rw_receipt_rate']
        reimbursement = per_diem + mileage + receipts

    elif trip_profile == 'ON_SITE':
        # Generous per-diem and receipts, almost no mileage reimbursement.
        per_diem = trip_duration_days * params['os_per_diem_rate']
        # Mileage is incidental, not rewarded.
        mileage = miles_traveled * params['os_mileage_rate']
        # More permissive on receipts, up to a daily cap.
        daily_spend = total_receipts_amount / trip_duration_days
        if daily_spend > params['os_receipt_daily_cap']:
             receipts = trip_duration_days * params['os_receipt_daily_cap'] * params['os_receipt_rate_capped']
        else:
             receipts = total_receipts_amount * params['os_receipt_rate_normal']
        reimbursement = per_diem + mileage + receipts

    elif trip_profile == 'PUNITIVE':
        # Heavily penalize trips that don't make sense.
        per_diem = trip_duration_days * params['pun_per_diem_rate']
        mileage = miles_traveled * params['pun_mileage_rate']
        receipts = total_receipts_amount * params['pun_receipt_rate']
        reimbursement = per_diem + mileage + receipts

    else: # STANDARD path (for trips between ON_SITE and ROAD_WARRIOR)
        per_diem = trip_duration_days * params['std_per_diem_rate']
        mileage = miles_traveled * params['std_mileage_rate']
        receipts = total_receipts_amount * params['std_receipt_rate']
        reimbursement = per_diem + mileage + receipts

    # ==========================================================================
    # 3. GLOBAL BONUSES & ADJUSTMENTS (Applied to most paths)
    # ==========================================================================
    # These are quirks of the system that apply regardless of the trip's main purpose.
    if trip_profile != 'PUNITIVE':
        # 5-day "Sweet Spot" Bonus
        if trip_duration_days == 5:
            reimbursement += params['global_bonus_5_day']

        # Rounding "Bug"
        receipt_cents = int(round(total_receipts_amount * 100)) % 100
        if receipt_cents in [49, 99]:
            reimbursement += params['global_bonus_rounding']

    return round(max(0, reimbursement), 2)