import pathlib, csv, ast, json
from colorama import Fore

def test(model):

    model = model()

    print('Loading emission factors...')
    emission_factor_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/item_emission_factors.py'

    with open(emission_factor_path, 'r') as f:
        emission_factors = ast.literal_eval(f.read()[19:]) 

    emission_factor_vectors = {emission_factor: model.get_embeddings(emission_factor)[0] for emission_factor in emission_factors.keys()}

    print('Starting test...')
    results = []
    total_correct = 0

    confusion_matrix = {}
    correct_items = []
    incorrect_items = []

    csv_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/omnivore.csv'
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        food_items = list(reader)

        calculated_co2e = 0
        estimated_co2e = 0
        total_spent = 0

        insufficient_data = []

        for line in food_items[1:]:
            # Food (Burners-Lee defined), CO2e per KG (BLd), price, item name (Tesco), £/kg, OPD category (defined by me)
            if all(line) and len(line) == 6:
                # Get the item embedding and find the best match
                item_embedding = model.get_embeddings(line[3])[0]
                best_match = model.get_item_from_vectors(item_embedding, *emission_factor_vectors.items())

                # Check if the best match is correct
                correct = best_match[0] == line[5]
                total_correct += correct
                results.append([line[3], best_match[0], line[5], correct])

                # CO2e estimation variables
                # Amount spent / cost per kg = amount in kg
                total_spent = round(total_spent + float(line[2]), 2)
                produce_kg = float(line[4])

                # Amount in kg * CO2e per kg = total CO2e
                calculated_co2e += produce_kg * float(line[1])
                estimated_co2e += produce_kg * float(emission_factors[best_match[0]])
                
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
            else:
                insufficient_data.append(line)
        
    # [print(result) for result in results]
    # print()
    print(f'Total:              {total_correct}/{len(results)}')
    print(f'Accuracy:           {round(total_correct / len(results), 2)}')
    print(f'Calculated CO2e:    {round(calculated_co2e, 2)}kg')
    print(f'Estimated CO2e:     {round(estimated_co2e, 2)}kg')
    print(f'Difference:         {round(calculated_co2e - estimated_co2e, 2)}kg')
    print(f'Error:              {round((calculated_co2e - estimated_co2e) / calculated_co2e, 2)}')
    print(f'Total spent:        £{total_spent}')
    print(f'Est. emission rate: {round(estimated_co2e / total_spent)} per £')
    print()
    print('Confusion matrix (true positive, false negative, false positive):')
    [print(item) for item in confusion_matrix.items()]
    print()
    # print('\nCorrect items:')
    # [print(item[0]) for item in correct_items]
    print('\nIncorrect items:')
    [print(f'{item[0]}\n{Fore.RED + item[1] + Fore.RESET}') for item in incorrect_items]
    print('\nInsufficient data:')
    [print(item) for item in insufficient_data]
    print(f'\nTotal items estimated: {len(correct_items + incorrect_items)} out of {len(food_items[1:])}')
