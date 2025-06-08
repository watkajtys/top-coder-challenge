# model.py (Version 11.0 - Neural Network with ReLU)
import math

def get_features(days, miles, receipts):
    # This function remains the same.
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
    normalized = {}
    for name, value in features.items():
        min_val = scaling_params[name]['min']
        max_val = scaling_params[name]['max']
        if (max_val - min_val) > 0:
            normalized[name] = (value - min_val) / (max_val - min_val)
        else:
            normalized[name] = 0.0
    return normalized

def relu(x):
    """The Rectified Linear Unit activation function."""
    return max(0, x)

def predict(features, weights):
    """
    Predicts using a simple two-layer neural network structure.
    features -> hidden_layer -> ReLU -> output
    """
    # --- Hidden Layer Calculation ---
    hidden_layer_values = [0.0] * weights['hidden_layer_size']
    for i in range(weights['hidden_layer_size']):
        # Calculate the value for each "neuron" in the hidden layer
        neuron_value = 0.0
        for feature_name, feature_value in features.items():
            # Each neuron has its own set of weights for each input feature
            neuron_value += feature_value * weights['w1'][feature_name][i]

        # Apply the ReLU activation function
        hidden_layer_values[i] = relu(neuron_value)

    # --- Output Layer Calculation ---
    output = 0.0
    for i in range(weights['hidden_layer_size']):
        # The final output is a weighted sum of the activated hidden layer values
        output += hidden_layer_values[i] * weights['w2'][i]

    return max(0, output)