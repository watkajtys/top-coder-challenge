# model_to_optimize.py (Version 5.1 - with Trip Profile)
import math

def calculate_reimbursement(trip_duration_days, miles_traveled, total_receipts_amount):
    if trip_duration_days <= 0: return 0.0
    trip_duration_days = int(trip_duration_days)
    miles_traveled = float(miles_traveled)
    total_receipts_amount = float(total_receipts_amount)

    daily_spend = total_receipts_amount / trip_duration_days if trip_duration_days > 0 else 0
    miles_per_day = miles_traveled / trip_duration_days if trip_duration_days > 0 else 0

    per_diem_total = 49.14278259156015 * trip_duration_days

    mileage_total = 0
    if trip_duration_days < 38.34697362593889:
        cutoff = -285.02840294993973
        if miles_traveled <= cutoff:
            mileage_total = miles_traveled * -0.28625989213057657
        else:
            mileage_total = (cutoff * -0.28625989213057657) + ((miles_traveled - cutoff) * 0.4395186601606763)
    else:
        mileage_total = miles_traveled * -1.7320189369392007

    receipt_reimbursement = 0
    if 0 < total_receipts_amount < 18.314213135058637:
        receipt_reimbursement = -120.83467527584385
    else:
        allowance_multiplier = 0.4072234007176816
        if daily_spend < -175.7447700852244:
            allowance_multiplier = 1.6373892048646406
        receipt_reimbursement = total_receipts_amount * allowance_multiplier

    adjustment = 0
    # Simulate a "Sales Trip Profile" with more aggressive bonuses
    if 0 == 1:
        if trip_duration_days < 38.34697362593889 and miles_per_day > 467.78018623977454:
            adjustment += (miles_per_day - 467.78018623977454) * 1.7681198173445467

    if trip_duration_days >= 38.34697362593889 and daily_spend > 192.94795706596307:
        adjustment -= (daily_spend - 192.94795706596307) * 21.852518796502462

    if trip_duration_days == 5:
        adjustment += 101.3638638781631

    if 8 <= trip_duration_days <= 10 and daily_spend <= 192.94795706596307:
        adjustment += 117.32544973383474

    receipt_cents = int(round(total_receipts_amount * 100)) % 100
    if receipt_cents in [49, 99]:
        adjustment += -216.4711050792443

    final_amount = per_diem_total + mileage_total + receipt_reimbursement + adjustment
    return round(max(0, final_amount), 2)
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python solution.py <days> <miles> <receipts>")
        sys.exit(1)
    try:
        duration = int(sys.argv[1])
        miles = float(sys.argv[2])
        receipts = float(sys.argv[3])
        result = calculate_reimbursement(duration, miles, receipts)
        print(result)
    except Exception:
        print(0.0)
        sys.exit(0)
