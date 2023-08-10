import pathlib, csv, ast
from colorama import Fore

def test(model):

    model = model()

    emission_factor_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/category_emission_factors.py'

    with open(emission_factor_path, 'r') as f:
        emission_factors = ast.literal_eval(f.read()[28:])

    emission_factor_vectors = {emission_factor: model.get_embeddings(emission_factor)[0] for emission_factor in emission_factors.keys()}
    # print(emission_factor_vectors['Meat and meat products (excl. poultry)'])

    csv_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/foodItems-categories-pricesPerKg.csv'

    results = []
    total_correct = 0

    confusion_matrix = {}
    correct_items = []
    incorrect_items = []

    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        food_items = list(reader)
        for line in food_items[1:]:
            # Food (Burners-Lee defined), CO2e per KG (BLd), price(ignore), item name (Tesco), £/kg, OPD category (defined by me)
            if line[5]:
                item_embedding = model.get_embeddings(line[3])[0]
                best_match = model.get_category_from_vectors(item_embedding, *emission_factor_vectors.items())

                correct = best_match[0] == line[5]
                total_correct += correct
                results.append([line[3], best_match[0], line[5], correct])

                if line[5] not in confusion_matrix.keys():
                    confusion_matrix[line[5]] = [0, 0]
                if correct:
                    confusion_matrix[line[5]][0] += 1
                    correct_items.append([line[3], best_match[0], line[5]])
                else:
                    confusion_matrix[line[5]][1] += 1
                    incorrect_items.append([line[3], best_match[0], line[5]])
        
        # [print(result) for result in results]
        print()
        print(f'Total:      {total_correct}/{len(results)}')
        print(f'Accuracy:   {round(total_correct / len(results), 2)}')
        print()
        [print(item) for item in confusion_matrix.items()]
        print('\nCorrect items:')
        [print(item[0]) for item in correct_items]
        print('\nIncorrect items:')
        [print(f'{Fore.RESET + item[0]}\n{Fore.RED + item[1]} | {Fore.GREEN + item[2]}') for item in incorrect_items]