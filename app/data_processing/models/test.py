import pathlib, csv, ast, json
from colorama import Fore

def test(model):

    model = model()

    emission_factor_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/item_emission_factors.py'

    with open(emission_factor_path, 'r') as f:
        emission_factors = ast.literal_eval(f.read()[19:]) 

    emission_factor_vectors = {emission_factor: model.get_embeddings(emission_factor)[0] for emission_factor in emission_factors.keys()}

    csv_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/foodItems-categories-pricesPerKg.csv'

    results = []
    total_correct = 0

    confusion_matrix = {}
    correct_items = []
    incorrect_items = []

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        food_items = list(reader)

        estimated_co2e = 0
        BL_co2e = 0

        total_spent = 0
        category_spend = {}

        for line in food_items[1:]:
            # Food (Burners-Lee defined), CO2e per KG (BLd), price, item name (Tesco), £/kg, OPD category (defined by me)
            if line[5]:
                # Get the item embedding and find the best match
                item_embedding = model.get_embeddings(line[3])[0]
                best_match = model.get_category_from_vectors(item_embedding, *emission_factor_vectors.items())

                # Check if the best match is correct
                correct = best_match[0] == line[5]
                total_correct += correct
                results.append([line[3], best_match[0], line[5], correct])

                # CO2e estimation variables
                # Amount spent / cost per kg = amount in kg
                amount_spent = float(line[2])
                cost_per_kg = float(line[4])
                produce_kg = amount_spent / cost_per_kg

                # Amount in kg * CO2e per kg = total CO2e
                BL_co2e += produce_kg * float(line[1])
                estimated_co2e += produce_kg * float(emission_factors[best_match[0]])
                
                # Add this purchase to the total spend
                total_spent = round(total_spent + float(line[2]), 2)
                if line[5] not in category_spend.keys():
                    category_spend[line[5]] = 0
                # category_spend[line[5]] = round(category_spend[line[5]] + float(line[2]), 2)
                
                # Add to the confusion matrix
                if line[5] not in confusion_matrix.keys():
                    confusion_matrix[line[5]] = [0, 0, 0]
                if best_match[0] not in confusion_matrix.keys():
                    confusion_matrix[best_match[0]] = [0, 0, 0]
                
                if correct:
                    confusion_matrix[line[5]][0] += 1
                    correct_items.append([line[3], best_match[0]]) #, line[5]])
                else:
                    confusion_matrix[line[5]][1] += 1
                    confusion_matrix[best_match[0]][2] += 1
                    incorrect_items.append([line[3], best_match[0]]) #, line[5]])
        
    # [print(result) for result in results]
    print()
    print(f'Total:      {total_correct}/{len(results)}')
    print(f'Accuracy:   {round(total_correct / len(results), 2)}')
    print()
    [print(item) for item in confusion_matrix.items()]
    print()
    print(f'Estimated CO2e: {estimated_co2e}kg')
    print(f'BL CO2e:        {BL_co2e}kg')
    print(f'Total spend:    £{total_spent}')
    print()
    # [print(f'{category}: £{spend}') for category, spend in category_spend.items()]
    print()
    print('\nCorrect items:')
    [print(item[0]) for item in correct_items]
    print('\nIncorrect items:')
    [print(f'{Fore.RESET + item[0]}\n{Fore.GREEN + item[1]}') for item in incorrect_items]
