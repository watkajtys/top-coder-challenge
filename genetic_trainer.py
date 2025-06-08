# genetic_trainer.py (Version 14.0 - Corrected and Enhanced)
import json, random, copy, sys
from model_rule_engine import calculate_reimbursement

def evaluate_fitness(chromosome, test_cases):
    total_error = 0.0
    for case in test_cases:
        inputs = case['input']
        expected = case['expected_output']
        prediction = calculate_reimbursement(
            inputs['trip_duration_days'], inputs['miles_traveled'], inputs['total_receipts_amount'], chromosome)
        total_error += abs(prediction - expected)

    mae = total_error / len(test_cases)
    return 1.0 / (mae + 1.0)

def crossover(parent1, parent2):
    child_chromosome = []
    for i in range(len(parent1)):
        # Ensure the essential 'type' and 'action' fields are preserved from one parent
        # to avoid nonsensical combinations.
        p1_gene = parent1[i]
        p2_gene = parent2[i]
        if random.random() < 0.5:
            child_chromosome.append(copy.deepcopy(p1_gene))
        else:
            child_chromosome.append(copy.deepcopy(p2_gene))
    return child_chromosome

def mutate(chromosome, mutation_rate=0.1):
    mutated_chromosome = copy.deepcopy(chromosome)
    for i in range(len(mutated_chromosome)):
        if random.random() < mutation_rate:
            gene = mutated_chromosome[i]
            # Choose a mutation type that is valid for the gene
            possible_mutations = []
            if 'value' in gene: possible_mutations.append('value')
            if 'amount' in gene: possible_mutations.append('amount')
            if 'op' in gene and gene['op'] in ['<', '>']: possible_mutations.append('operator')
            if 'enabled' in gene: possible_mutations.append('enabled')
            if not possible_mutations: continue

            mutation_type = random.choice(possible_mutations)

            if mutation_type in ['value', 'amount']:
                # Nudge numeric values
                change_factor = random.uniform(0.8, 1.2)
                gene[mutation_type] *= change_factor
            elif mutation_type == 'operator':
                gene['op'] = '<' if gene['op'] == '>' else '>'
            elif mutation_type == 'enabled':
                gene['enabled'] = not gene.get('enabled', True)
    return mutated_chromosome

def generate_final_script(chromosome):
    final_code = "import sys\nimport math\n\n"
    final_code += f"chromosome = {json.dumps(chromosome, indent=4)}\n\n"
    with open('model_rule_engine.py', 'r') as f:
        final_code += f.read()

    main_block = """
if __name__ == "__main__":
    if len(sys.argv) != 4: sys.exit(1)
    try:
        result = calculate_reimbursement(int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), chromosome)
        print(f"{result:.2f}")
    except Exception: print(0.0)
"""
    with open('solution.py', 'w') as f: f.write(final_code + main_block)
    print("\n✅ Generated final 'solution.py' with evolved rule set.")

if __name__ == "__main__":
    with open('public_cases.json', 'r') as f: test_cases = json.load(f)

    # A much more detailed "Genesis" chromosome based on our best manual model.
    # This gives the GA a much stronger starting point.
    genesis_chromosome = [
        # Base per diem and mileage
        {'feature': 'days', 'op': '>', 'value': 0, 'action': 'add_per_day', 'amount': 100.0, 'enabled': True},
        {'feature': 'miles', 'op': '>', 'value': 100, 'action': 'add_per_mile', 'amount': 0.5, 'enabled': True},
        {'feature': 'miles', 'op': '<', 'value': 101, 'action': 'add_per_mile', 'amount': 0.7, 'enabled': True},

        # Base receipt handling
        {'feature': 'receipts', 'op': '>', 'value': 0, 'action': 'mult_feature', 'amount': 0.85, 'enabled': True},

        # Punitive Rules
        {'feature': 'daily_spend', 'op': '>', 'value': 300, 'action': 'add_amount', 'amount': -500.0, 'enabled': True},
        {'feature': 'miles_per_day', 'op': '>', 'value': 600, 'action': 'add_amount', 'amount': -300.0, 'enabled': True},

        # Bonus Rules
        {'feature': 'days', 'op': '==', 'value': 5, 'action': 'add_amount', 'amount': 75.0, 'enabled': True},
        {'feature': 'miles_per_day', 'op': '>', 'value': 200, 'action': 'add_amount', 'amount': 50.0, 'enabled': True},
        {'feature': 'miles_per_day', 'op': '<', 'value': 50, 'action': 'add_amount', 'amount': -100.0, 'enabled': True},
    ]

    POPULATION_SIZE = 100
    NUM_GENERATIONS = 250
    ELITISM_COUNT = 10
    MUTATION_RATE = 0.1

    print("🧬 Starting Genetic Algorithm Training...")
    population = [mutate(genesis_chromosome, mutation_rate=0.7) for _ in range(POPULATION_SIZE)] # Start with diverse population

    for gen in range(NUM_GENERATIONS):
        pop_with_fitness = sorted(
            [(chromo, evaluate_fitness(chromo, test_cases)) for chromo in population],
            key=lambda x: x[1], reverse=True
        )

        best_fitness = pop_with_fitness[0][1]
        best_mae = (1.0 / best_fitness) - 1.0
        print(f"Generation {gen+1}/{NUM_GENERATIONS} | Best MAE: ${best_mae:.2f}")

        new_population = [item[0] for item in pop_with_fitness[:ELITISM_COUNT]]

        # Create the rest of the new generation
        while len(new_population) < POPULATION_SIZE:
            parent1 = random.choice(pop_with_fitness[:POPULATION_SIZE//2])[0]
            parent2 = random.choice(pop_with_fitness[:POPULATION_SIZE//2])[0]
            child = crossover(parent1, parent2)
            child = mutate(child, MUTATION_RATE)
            new_population.append(child)

        population = new_population

    final_fitness_scores = [(p, evaluate_fitness(p, test_cases)) for p in population]
    best_chromosome = sorted(final_fitness_scores, key=lambda x: x[1], reverse=True)[0][0]

    print("\n🏁 Training Complete.")
    generate_final_script(best_chromosome)