import sys
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    """
    Calculates reimbursement based on a detailed, reverse-engineered model of the
    ACME system. This version uses a decision-tree structure with specific
    calculation paths for different trip profiles.
    """

    if trip_duration_days <= 0:
        return 0.0

    # ==========================================================================
    # 1. DERIVED METRICS
    # ==========================================================================
    daily_spend_rate = total_receipts_amount / trip_duration_days
    miles_per_day = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0

    # ==========================================================================
    # 2. DECISION TREE TO DETERMINE CALCULATION PATH
    # ==========================================================================
    # The system uses fundamentally different models based on trip characteristics.
    # The most critical factor is excessive spending, which triggers penalties.

    # --- PATH A: Punitive path for short, extremely expensive trips ---
    # Catches cases like Case 152 (4 days, $2321 receipts)
    if trip_duration_days <= 4 and daily_spend_rate > 250:
        # Per diem is nullified and replaced by a low flat amount.
        per_diem_component = 150.0
        # Mileage rate is drastically reduced.
        mileage_component = miles_traveled * 0.20
        # Receipts are not reimbursed but are used to calculate a penalty.
        receipt_penalty = (daily_spend_rate - 250) * 1.5
        receipt_component = -receipt_penalty

        reimbursement = per_diem_component + mileage_component + receipt_component
        return round(max(0, reimbursement), 2) # Ensure it doesn't go below zero

    # --- PATH B: "Vacation Penalty" for long trips with high spending ---
    # As described by Kevin. Catches cases like Case 684 (8 days, $1645 receipts)
    if trip_duration_days >= 8 and daily_spend_rate > 90:
        # Standard per diem.
        per_diem_component = trip_duration_days * 110.0
        # Mileage rate is standard.
        mileage_component = miles_traveled * 0.50
        # The key is that receipts are *penalized* instead of reimbursed.
        # The penalty is a percentage of the amount over the daily limit.
        overage = (total_receipts_amount - (trip_duration_days * 90))
        receipt_component = - (overage * 0.8)

        reimbursement = per_diem_component + mileage_component + receipt_component
        return round(max(0, reimbursement), 2)

    # --- PATH C: Standard Calculation for all other trips ---
    # This is the default path if no penalty paths are triggered.
    else:
        # C1: Per Diem Component
        per_diem_component = trip_duration_days * 100.0

        # C2: Mileage Component (Tiered Rate)
        mileage_component = 0
        if miles_traveled > 500:
            mileage_component = (100 * 0.70) + (400 * 0.60) + ((miles_traveled - 500) * 0.50)
        elif miles_traveled > 100:
            mileage_component = (100 * 0.70) + ((miles_traveled - 100) * 0.60)
        else:
            mileage_component = miles_traveled * 0.70

        # C3: Receipt Component (Standard Reimbursement, with small receipt penalty)
        if total_receipts_amount < 25 and trip_duration_days > 1:
             # Penalty for very low receipts on multi-day trips, as mentioned by Lisa/Dave.
            receipt_component = -25.0
        else:
            receipt_component = total_receipts_amount * 0.80

        # C4: Bonuses and Fine-Tuning Adjustments
        bonus_adjustment = 0
        # 5-day trip bonus
        if trip_duration_days == 5:
            bonus_adjustment += 50.0
        # Efficiency bonus
        if 150 < miles_per_day < 250:
            bonus_adjustment += 35.0
        # "Rounding bug" from Lisa's interview
        if str(total_receipts_amount).endswith('.49') or str(total_receipts_amount).endswith('.99'):
            bonus_adjustment += 5.51

        reimbursement = (
            per_diem_component +
            mileage_component +
            receipt_component +
            bonus_adjustment
        )
        return round(reimbursement, 2)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python solution.py <trip_duration_days> <miles_traveled> <total_receipts_amount>")
        sys.exit(1)

    try:
        duration = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])

        result = calculate_reimbursement(duration, miles, receipts)
        print(result)

    except (ValueError, ZeroDivisionError):
        # Handle invalid inputs gracefully.
        print(0.0)
        sys.exit(0)