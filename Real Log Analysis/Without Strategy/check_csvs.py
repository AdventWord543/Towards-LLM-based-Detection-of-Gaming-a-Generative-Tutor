import csv

def check_csv(filepath, expected_count=94):
    """Check CSV for duplicates and missing/extra entries."""

    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Extract filenames
    filenames = [row[0] for row in rows if row and row[0].strip()]

    # Check for duplicates
    seen = set()
    duplicates = []
    for fn in filenames:
        if fn in seen:
            duplicates.append(fn)
        seen.add(fn)

    print(f"\n{filepath}:")
    print(f"  Row count: {len(filenames)} (expected: {expected_count})")

    if len(filenames) != expected_count:
        diff = len(filenames) - expected_count
        print(f"  WARNING: {'+' if diff > 0 else ''}{diff} rows")

    if duplicates:
        print(f"  DUPLICATES: {duplicates}")
    else:
        print(f"  No duplicates found")

    return set(filenames)


# Check all files and collect their filename sets
files = ['Run1.csv', 'Run2.csv', 'Run3.csv', 'Run4.csv', 'Run5.csv', 'Run6.csv', 'Run7.csv', 'Run8.csv', 'Run9.csv', 'Run10.csv']
all_sets = {}

for filename in files:
    all_sets[filename] = check_csv(filename)

# Compare files to find missing entries between them
print("\n" + "="*50)
print("Cross-file comparison:")
print("="*50)

# Get union of all filenames
all_filenames = set()
for s in all_sets.values():
    all_filenames.update(s)

print(f"\nTotal unique filenames across all files: {len(all_filenames)}")

# Check which files are missing from each CSV
for filename, file_set in all_sets.items():
    missing = all_filenames - file_set
    extra = file_set - all_filenames  # This will always be empty by definition
    if missing:
        print(f"\n{filename} missing ({len(missing)}):")
        for m in sorted(missing, key=lambda x: int(x.split('.')[0])):
            print(f"  - {m}")
