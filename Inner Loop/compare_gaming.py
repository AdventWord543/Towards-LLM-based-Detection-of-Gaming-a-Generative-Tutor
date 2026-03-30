import csv

filename_gaming_file = "filename_gaming.csv"
truth_file = "Inner Loop Truth.csv"

# Read filename_gaming.csv
filename_data = {}
with open(filename_gaming_file, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Strip .txt to match ID format
        file_id = row["Filename"].replace(".txt", "")
        # Count non-empty Gaming values
        count = 0
        i = 1
        while f"Gaming{i}" in row:
            val = row[f"Gaming{i}"]
            if val and val.strip():
                count += 1
            i += 1
        filename_data[file_id] = count

# Read truth file
truth_data = {}
with open(truth_file, "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        file_id = row["ID"]
        # Count non-empty Round values
        count = 0
        i = 1
        while f"Round{i}_Gaming" in row:
            val = row[f"Round{i}_Gaming"]
            if val and val.strip():
                count += 1
            i += 1
        truth_data[file_id] = count

# Compare counts
mismatches = []
matches = 0

for file_id in truth_data:
    truth_count = truth_data[file_id]
    test_count = filename_data.get(file_id, 0)

    if truth_count == test_count:
        matches += 1
    else:
        mismatches.append({
            "ID": file_id,
            "Truth_Rounds": truth_count,
            "Test_Rounds": test_count
        })

# Check for IDs in test but not in truth
for file_id in filename_data:
    if file_id not in truth_data:
        mismatches.append({
            "ID": file_id,
            "Truth_Rounds": "(not in truth)",
            "Test_Rounds": filename_data[file_id]
        })

# Report
print(f"=== Cell Count Comparison ===")
print(f"IDs with matching round counts: {matches}")
print(f"IDs with mismatched round counts: {len(mismatches)}")

if mismatches:
    print(f"\n=== Mismatches ===")
    for m in mismatches:
        print(f"  {m['ID']}: Truth={m['Truth_Rounds']}, Test={m['Test_Rounds']}")

    # Write mismatches to text file
    with open("cell_count_mismatches.txt", "w", encoding="utf-8") as f:
        f.write("Cell Count Mismatches\n")
        f.write("=" * 40 + "\n\n")
        for m in mismatches:
            f.write(f"{m['ID']}: Truth={m['Truth_Rounds']}, Test={m['Test_Rounds']}\n")
    print(f"\nMismatches written to cell_count_mismatches.txt")
else:
    print("\nAll IDs have the same number of filled cells!")
