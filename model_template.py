# model_template.py
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount, params):
    if trip_duration_days <= 0: return 0.0
    trip_duration_days = int(trip_duration_days)
    miles_traveled = float(miles_traveled)
    total_receipts_amount = float(total_receipts_amount)

    daily_spend_rate = total_receipts_amount / trip_duration_days if trip_duration_days > 0 else 0
    miles_per_day = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0

    if trip_duration_days == 1 and daily_spend_rate > params['p1_spend_threshold']:
        if miles_per_day >= params['p1_super_ultra_miles_threshold']:
            reimbursement = params['p1_per_diem_a'] + (miles_traveled * params['p1_mileage_rate_a']) + (total_receipts_amount * params['p1_receipt_rate_a'])
        elif miles_per_day >= params['p1_ultra_miles_threshold']:
            reimbursement = params['p1_per_diem_b'] + (miles_traveled * params['p1_mileage_rate_b']) + (total_receipts_amount * params['p1_receipt_rate_b'])
        else:
            effective_receipts = min(total_receipts_amount, params['p1_receipt_cap_c'])
            reimbursement = params['p1_per_diem_c'] + (miles_traveled * params['p1_mileage_rate_c']) + (effective_receipts * params['p1_receipt_rate_c'])
        return round(max(0, reimbursement), 2)

    elif 2 <= trip_duration_days <= 4 and daily_spend_rate > params['p2_spend_threshold'] and miles_per_day < params['p2_miles_per_day_threshold']:
        effective_receipts = min(total_receipts_amount, trip_duration_days * params['p2_daily_receipt_cap'])
        reimbursement = params['p2_per_diem'] + (miles_traveled * params['p2_mileage_rate']) + (effective_receipts * params['p2_receipt_rate'])
        return round(max(0, reimbursement), 2)

    elif 2 <= trip_duration_days <= 7 and daily_spend_rate > params['p3_spend_threshold']:
        bonus_adjustment = 0
        per_diem_component = trip_duration_days * params['p3_per_diem_rate']
        mileage_component = miles_traveled * params['p3_mileage_rate']
        receipt_component = total_receipts_amount * params['p3_receipt_rate']
        if trip_duration_days == 5: bonus_adjustment += params['p_all_bonus_5_day']
        if params['p_all_eff_bonus_min'] < miles_per_day < params['p_all_eff_bonus_max']: bonus_adjustment += params['p_all_eff_bonus_amount']
        if str(total_receipts_amount).endswith('.49') or str(total_receipts_amount).endswith('.99'): bonus_adjustment += params['p_all_rounding_bug_bonus']
        reimbursement = per_diem_component + mileage_component + receipt_component + bonus_adjustment
        return round(max(0, reimbursement), 2)

    elif trip_duration_days >= 12 and daily_spend_rate < params['p4_spend_threshold'] and miles_per_day < params['p4_miles_per_day_threshold']:
        reimbursement = params['p4_per_diem_flat'] + (miles_traveled * params['p4_mileage_rate']) + (total_receipts_amount * params['p4_receipt_rate'])
        return round(max(0, reimbursement), 2)

    elif trip_duration_days >= 8 and daily_spend_rate > params['p5_spend_threshold']:
        effective_receipts = min(total_receipts_amount, trip_duration_days * params['p5_daily_receipt_cap'])
        reimbursement = (trip_duration_days * params['p5_per_diem_rate']) + (miles_traveled * params['p5_mileage_rate']) + (effective_receipts * params['p5_receipt_rate'])
        return round(max(0, reimbursement), 2)

    else: # DEFAULT PATH
        per_diem_component = trip_duration_days * params['def_per_diem_rate']

        miles_in_tier1 = min(miles_traveled, params['def_mileage_tier1_cutoff'])
        mileage_component = miles_in_tier1 * params['def_mileage_rate_t1']
        if miles_traveled > params['def_mileage_tier1_cutoff']:
            miles_in_tier2 = min(miles_traveled - params['def_mileage_tier1_cutoff'], params['def_mileage_tier2_cutoff'] - params['def_mileage_tier1_cutoff'])
            mileage_component += miles_in_tier2 * params['def_mileage_rate_t2']
        if miles_traveled > params['def_mileage_tier2_cutoff']:
            miles_in_tier3 = miles_traveled - params['def_mileage_tier2_cutoff']
            mileage_component += miles_in_tier3 * params['def_mileage_rate_t3']

        if total_receipts_amount < params['def_small_receipt_threshold'] and trip_duration_days > 1:
            receipt_component = params['def_small_receipt_penalty']
        else:
            receipt_component = total_receipts_amount * params['def_receipt_rate']

        bonus_adjustment = 0
        if trip_duration_days == 5: bonus_adjustment += params['p_all_bonus_5_day']
        if params['p_all_eff_bonus_min'] < miles_per_day < params['p_all_eff_bonus_max']: bonus_adjustment += params['p_all_eff_bonus_amount']
        if str(total_receipts_amount).endswith('.49') or str(total_receipts_amount).endswith('.99'): bonus_adjustment += params['p_all_rounding_bug_bonus']

        reimbursement = per_diem_component + mileage_component + receipt_component + bonus_adjustment
        return round(reimbursement, 2)