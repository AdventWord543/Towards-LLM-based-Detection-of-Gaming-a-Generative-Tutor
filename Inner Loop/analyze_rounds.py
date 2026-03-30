import csv

# Read the CSV file
with open('filename_gaming.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

# Filter for scenarios 01 through 14
target_scenarios = [f'{i:02d}' for i in range(1, 15)]  # 01, 02, ..., 14

all_matching_rows = []

for row in rows:
    if not row:
        continue
    filename = row[0]
    # Extract scenario number (first part before the dot)
    if '.' in filename:
        scenario = filename.split('.')[0]
        # Normalize to 2 digits
        if len(scenario) == 1:
            scenario = '0' + scenario
        if scenario in target_scenarios:
            all_matching_rows.append(row)

# Count files with values for each round (total across scenarios 01-14)
print(f"Total files (scenarios 01-14): {len(all_matching_rows)}\n")
print("Round breakdown (number of files with a value in each round):\n")

round_counts = {}
for round_num in range(1, 11):
    count = 0
    for row in all_matching_rows:
        if len(row) > round_num and row[round_num].strip():
            count += 1
    if count > 0:
        round_counts[round_num] = count

for round_num, count in round_counts.items():
    print(f"Round {round_num}: {count} files")
