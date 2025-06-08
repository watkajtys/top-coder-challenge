# model.py (Version 10.0 - Normalization-Aware)
import math

def get_features(days, miles, receipts):
    """Calculates raw, unscaled features."""
    features = {}
    features['days'] = float(days)
    features['miles'] = float(miles)
    features['receipts'] = float(receipts)
    features['daily_miles'] = miles / days if days > 0 else 0
    features['daily_spend'] = receipts / days if days > 0 else 0
    features['days_sq'] = features['days'] ** 2
    features['miles_sq'] = features['miles'] ** 2
    features['receipts_sq'] = features['receipts'] ** 2
    features['miles_x_days'] = features['miles'] * features['days']
    features['receipts_x_days'] = features['receipts'] * features['days']
    features['is_long_trip'] = 1.0 if days >= 8 else 0.0
    features['is_short_trip'] = 1.0 if days <= 3 else 0.0
    features['is_5_day_trip'] = 1.0 if days == 5 else 0.0
    features['is_hyper_efficient'] = 1.0 if features['daily_miles'] > 400 else 0.0
    features['is_high_spend'] = 1.0 if features['daily_spend'] > 150 else 0.0
    features['has_small_receipts'] = 1.0 if 0 < receipts < 25 else 0.0
    features['bias'] = 1.0
    return features

def normalize_features(features, scaling_params):
    """Applies Min-Max scaling to a feature set."""
    normalized = {}
    for name, value in features.items():
        min_val = scaling_params[name]['min']
        max_val = scaling_params[name]['max']
        if (max_val - min_val) > 0:
            normalized[name] = (value - min_val) / (max_val - min_val)
        else:
            normalized[name] = 0 # Feature is constant, scale to 0
    return normalized

def predict(features, weights):
    """Calculates a prediction from a set of (already normalized) features."""
    prediction = 0.0
    for name, value in features.items():
        if name in weights:
            prediction += value * weights[name]
    return max(0, prediction)