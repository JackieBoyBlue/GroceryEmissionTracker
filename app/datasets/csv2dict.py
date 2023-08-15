import csv
import os

emission_factors = {}

with open("app/datasets/EmissionFactorDatabase-Wrap-simplified.csv", "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.reader(f)
    for row in reader:
        emission_factors[row[0]] = float(row[1])

with open(f"{os.path.dirname(os.path.realpath(__file__))}/item_emission_factors.py", "w", encoding="utf-8") as f:
    f.write(f'emission_factors = {emission_factors}\n')
