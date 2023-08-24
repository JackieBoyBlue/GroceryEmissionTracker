import pathlib, csv, ast, json
from colorama import Fore
import random

def test(model):

    model = model()

    print('Loading emission factors...')
    emission_factor_path = pathlib.Path(__file__).parent.parent.parent / 'datasets/item_emission_factors.py'

    with open(emission_factor_path, 'r') as f:
        emission_factors = ast.literal_eval(f.read()[19:]) 

    emission_factor_vectors = {emission_factor: model.get_embeddings(emission_factor)[0] for emission_factor in emission_factors.keys()}
    category_emission_factor = 0.51748

    for diet in ['omnivore', 'vegetarian-replace', 'vegetarian-remove', 'vegan-replace', 'vegan-remove']:
    # for diet in ['omnivore']:
        print(diet.upper())
        # EMBEDDING ESTIMATION TEST
        print('Starting embedding test...')
        results = []
        total_correct = 0

        correct_items = []
        incorrect_items = []
        
        # Set up confusion matrix for multiclass classification
        emission_factor_vector_keys = list(emission_factor_vectors.keys())
        n_classifications = len(emission_factor_vector_keys)
        confusion_matrix = [[0 for _ in range(n_classifications)] for _ in range(n_classifications)]

        csv_path = pathlib.Path(__file__).parent.parent.parent / f'datasets/{diet}.csv'
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            food_items = list(reader)

            calculated_co2e = 0
            emedding_estimate = 0
            total_spent = 0

            insufficient_data = []

            for line in food_items[1:]:
                # Food (Defra), CO2e per KG (WRAP), price, item name (Tesco), kg, WRAP classification
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
                    calculated_co2e = round(calculated_co2e + produce_kg * float(line[1]), 5)
                    emedding_estimate = round(emedding_estimate + produce_kg * float(emission_factors[best_match[0]]), 5)
                    
                    # Add to confusion matrix
                    predicted = emission_factor_vector_keys.index(line[5])
                    estimated = emission_factor_vector_keys.index(best_match[0])
                    confusion_matrix[predicted][estimated] += 1

                    if correct:
                        correct_items.append([line[3], best_match[0]]) #, line[5]])
                    else:
                        incorrect_items.append([line[3], best_match[0]]) #, line[5]])
                else:
                    insufficient_data.append(line)

            # Calculate the accuracy, precision, recall and f1 score
            total_true_positives = 0
            total_false_positives = 0
            total_false_negatives = 0

            for row in range(n_classifications):
                for column in range(n_classifications):
                    if row == column:
                        total_true_positives += confusion_matrix[row][column]
                    else:
                        total_false_positives += confusion_matrix[column][row]
                        total_false_negatives += confusion_matrix[row][column]

            accuracy = round(total_correct / len(results), 2)

            # Precision = (TruePositives_1 + TruePositives_2) / ((TruePositives_1 + TruePositives_2) + (FalsePositives_1 + FalsePositives_2) )
            precision = (total_true_positives / (total_true_positives + total_false_positives))
            
            # Recall = (TruePositives_1 + TruePositives_2) / ((TruePositives_1 + TruePositives_2) + (FalseNegatives_1 + FalseNegatives_2))
            recall = round(total_true_positives / (total_true_positives + total_false_negatives), 2)

            # F-Measure = (2 * Precision * Recall) / (Precision + Recall)
            f1 = (2 * precision * recall) / (precision + recall)
            

            # USER-MERCHANT HISTORY ESTIMATION TEST
            print('Starting user-merchant test...')
            transactions = {}

            # Produce 20 baskets of random items
            for n in range(1, 51):
                transactions[n] = []
                for line in food_items[1:]:
                    if all(line) and len(line) == 6:
                        if random.random() < 0.25:
                            transactions[n].append(line)
            
            # Remove half to test.
            new_transactions = {}
            for n in range(1, 26):
                new_transactions[n] = transactions.pop(n)
            # The other half acts as a transaction history
            transaction_history = transactions

            # Iterate through the transaction history and get the estimate and cost for each
            estimate_history = {}
            for basket in transaction_history.items():
                # Half a chance of embedding estimation
                if random.random() < 0.5:
                    estimate = 0
                    cost = 0
                    for item in basket[1]:
                            item_embedding = model.get_embeddings(item[3])[0]
                            best_match = model.get_item_from_vectors(item_embedding, *emission_factor_vectors.items())
                            factor = float(emission_factors[best_match[0]])
                            estimate += float(item[4]) * factor
                            cost += float(item[2])
                    estimate_history[basket[0]] = (estimate, cost)
                # Half chance of MCC estimation
                else:
                    cost = sum([float(item[2]) for item in basket[1]])
                    estimate = cost * category_emission_factor
                    estimate_history[basket[0]] = (estimate, cost)
            
            # Get the average historic emission factor in CO2e/£ spent
            historic_emissions = sum(value[0] for value in estimate_history.values())
            historic_cost = sum(value[1] for value in estimate_history.values())
            user_merchant_factor = historic_emissions / historic_cost

            # Get the estimated and actual co2e for the target baskets
            basket_est_and_act = []

            for new_transaction in new_transactions.values():
                target_basket_cost = 0
                target_basket_co2e = 0
                for item in new_transaction:
                    target_basket_cost += float(item[2])
                    target_basket_co2e += float(item[1]) * float(item[4])
                basket_est_and_act.append((target_basket_cost * user_merchant_factor, target_basket_co2e))
            
            # Get the average estimate and 
            user_merchant_estimate = sum([estimate[0] for estimate in basket_est_and_act]) / len(basket_est_and_act)
            average_basket_co2e = sum([estimate[1] for estimate in basket_est_and_act]) / len(basket_est_and_act)


            # MCC ESTIMATION TEST
            print('Starting MCC test...')
            # mcc_estimate = round(target_basket_cost * category_emission_factor, 5)
            mcc_estimates = []
            for new_transaction in new_transactions.values():
                target_basket_cost = 0
                for item in new_transaction:
                    target_basket_cost += float(item[2])
                mcc_estimates.append(target_basket_cost * category_emission_factor)
            mcc_estimate = sum(mcc_estimates) / len(mcc_estimates)
                
            
        print('\nResults:\n')

        print('\n~~~      Embedding      ~~~')
        print(f'Target CO2e:        {round(calculated_co2e, 2)}kg')
        print(f'Embedding estimate: {round(emedding_estimate, 2)}kg')
        print(f'Difference:         {round(emedding_estimate - calculated_co2e, 2)}kg')
        print(f'Error:              {round((emedding_estimate / calculated_co2e) -1, 2)}')
        print(f'Total:              {total_correct}/{len(results)}')
        print(f'Accuracy:           {round(accuracy, 2)}')
        print(f'Precision:          {round(precision, 2)}')
        print(f'Recall:             {round(recall, 2)}')
        print(f'F1:                 {round(f1, 2)}')

        print('\n~~~User-Merchant History~~~')
        print(f'Target CO2e:        {round(average_basket_co2e, 2)}kg')
        print(f'User-Merchant est.: {round(user_merchant_estimate, 2)}kg')
        print(f'Difference:         {round(user_merchant_estimate - average_basket_co2e, 2)}kg')
        print(f'Error:              {round((user_merchant_estimate / average_basket_co2e) -1, 2)}')

        print('\n~~~         MCC         ~~~')
        print(f'Target CO2e:        {round(average_basket_co2e, 2)}kg')
        print(f'MCC rate est.:      {round(mcc_estimate, 2)}kg')
        print(f'Difference:         {round(mcc_estimate - average_basket_co2e, 2)}kg')
        print(f'Error:              {round((mcc_estimate / average_basket_co2e) -1, 2)}')
        print('\nEnd of test.\n\n')



    # print(f'Target CO2e:        {round(calculated_co2e, 2)}kg')
    # print(f'Estimated CO2e:     {round(estimated_co2e, 2)}kg')
    # print(f'Difference:         {round(calculated_co2e - estimated_co2e, 2)}kg')
    # print(f'Error:              {round((estimated_co2e - calculated_co2e) / calculated_co2e, 2)}')
    # print()
    # print(f'MCC rate est.:      {mcc_estimate}kg')
    # print(f'Diff. to 1st est.:  {round(mcc_estimate - estimated_co2e, 2)}kg')
    # print(f'Error:              {round((estimated_co2e - mcc_estimate) / mcc_estimate, 2)}')
    # print(f'Diff. to calc.:     {round(mcc_estimate - calculated_co2e, 2)}kg')
    # print(f'Error:              {round((calculated_co2e - mcc_estimate) / mcc_estimate, 2)}')
    # print(f'')
    # # print(f'Est. emission rate: {round(estimated_co2e / total_spent, 5)} per £')
    # print()
    # print('Confusion matrix (true positive, false negative, false positive):')
    # [print(item) for item in confusion_matrix.items()]
    # # print()
    # # print('\nCorrect items:')
    # # [print(item[0]) for item in correct_items]
    # print('\nIncorrect items:')
    # [print(f'{item[0]}\n{Fore.RED + item[1] + Fore.RESET}') for item in incorrect_items]
    # # print('\nInsufficient data:')
    # # [print(item) for item in insufficient_data]
    # print(f'\nTotal items estimated: {len(correct_items + incorrect_items)} out of {len(food_items[1:])}')
