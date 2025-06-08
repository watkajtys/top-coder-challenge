# trainer.py (Version 12.0 - Gradient Descent with INPUT and OUTPUT Normalization)
import json, random, math, sys
from model import get_features, normalize_features, predict, relu

if __name__ == "__main__":
    # --- 1. Load Data ---
    with open('public_cases.json', 'r') as f:
        data = json.load(f)

    # --- 2. Analyze & Normalize INPUTS (Features) ---
    print("Step 1: Normalizing inputs...")
    feature_names = get_features(1,1,1).keys()
    scaling_params = {name: {'min': float('inf'), 'max': float('-inf')} for name in feature_names}
    for case in data:
        features = get_features(case['input']['trip_duration_days'], case['input']['miles_traveled'], case['input']['total_receipts_amount'])
        for name, value in features.items():
            scaling_params[name]['min'] = min(scaling_params[name]['min'], value)
            scaling_params[name]['max'] = max(scaling_params[name]['max'], value)

    # --- 3. Analyze & Normalize OUTPUTS (Targets) ---
    print("Step 2: Normalizing outputs...")
    output_min = min(c['expected_output'] for c in data)
    output_max = max(c['expected_output'] for c in data)
    output_scaling_params = {'min': output_min, 'max': output_max}
    output_range = output_max - output_min

    # --- 4. Prepare Full Training Set with Scaled Data ---
    training_set = []
    for case in data:
        raw_features = get_features(case['input']['trip_duration_days'], case['input']['miles_traveled'], case['input']['total_receipts_amount'])
        normalized_features = normalize_features(raw_features, scaling_params)

        # Scale the expected output to a 0-1 range
        scaled_expected = (case['expected_output'] - output_min) / output_range if output_range > 0 else 0

        training_set.append({'features': normalized_features, 'expected': scaled_expected})
    print("Data preparation complete.")

    # --- 5. Initialize Model & Hyperparameters ---
    HIDDEN_LAYER_SIZE = 16 # A slightly larger hidden layer for more capacity
    weights = {
        'hidden_layer_size': HIDDEN_LAYER_SIZE,
        'w1': {fname: [random.uniform(-0.1, 0.1) for _ in range(HIDDEN_LAYER_SIZE)] for fname in feature_names},
        'w2': [random.uniform(-0.1, 0.1) for _ in range(HIDDEN_LAYER_SIZE)]
    }

    LEARNING_RATE = 0.1 # We can use a much healthier learning rate now
    NUM_EPOCHS = 30000

    print(f"\nStep 3: Starting training... (Learning Rate: {LEARNING_RATE}, Epochs: {NUM_EPOCHS})")

    # --- 6. The Training Loop ---
    for epoch in range(NUM_EPOCHS):
        total_squared_error = 0.0

        for item in training_set:
            features = item['features']
            scaled_expected = item['expected']

            # Forward Pass
            hidden_inputs = [sum(features[fn] * weights['w1'][fn][i] for fn in feature_names) for i in range(HIDDEN_LAYER_SIZE)]
            hidden_outputs = [relu(x) for x in hidden_inputs]
            scaled_prediction = sum(hidden_outputs[i] * weights['w2'][i] for i in range(HIDDEN_LAYER_SIZE))

            # Backpropagation
            error = scaled_prediction - scaled_expected
            total_squared_error += error ** 2

            grad_w2 = [hidden_outputs[i] * error for i in range(HIDDEN_LAYER_SIZE)]

            grad_w1_deltas = [(weights['w2'][i] * error) for i in range(HIDDEN_LAYER_SIZE)]

            for i in range(HIDDEN_LAYER_SIZE):
                if hidden_inputs[i] > 0: # ReLU derivative
                    weights['w2'][i] -= LEARNING_RATE * grad_w2[i]
                    for fn in feature_names:
                        weights['w1'][fn][i] -= LEARNING_RATE * features[fn] * grad_w1_deltas[i]

        if (epoch + 1) % 1000 == 0:
            # Note: This RMSE is on the SCALED data (0-1 range), so it will be very small.
            scaled_rmse = math.sqrt(total_squared_error / len(training_set))
            # We convert it back to dollar error for an intuitive progress report.
            dollar_rmse = scaled_rmse * output_range
            print(f"Epoch {epoch+1}/{NUM_EPOCHS} | Dollar RMSE: ${dollar_rmse:.2f}")

    print("\n🏁 Training Complete.")

    # --- 7. Generate Final Submission Script ---
    with open('model.py', 'r') as f: model_code = f.read()
    main_block = f"""
if __name__ == "__main__":
    import sys
    # --- OPTIMIZED WEIGHTS AND SCALING PARAMS ---
    weights = {json.dumps(weights, indent=4)}
    scaling_params = {json.dumps(scaling_params, indent=4)}
    output_scaling_params = {json.dumps(output_scaling_params, indent=4)}

    if len(sys.argv) != 4: sys.exit(1)
    try:
        raw_features = get_features(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]))
        norm_features = normalize_features(raw_features, scaling_params)

        # Predict the SCALED value
        scaled_result = predict(norm_features, weights)

        # De-normalize the result back to a dollar amount
        output_range = output_scaling_params['max'] - output_scaling_params['min']
        final_result = (scaled_result * output_range) + output_scaling_params['min']

        print(f"{{final_result:.2f}}")
    except Exception: print(0.0); sys.exit(0)
"""
    with open('solution.py', 'w') as f: f.write(model_code + main_block)
    print("✅ Generated final 'solution.py' with learned weights and scaling.")