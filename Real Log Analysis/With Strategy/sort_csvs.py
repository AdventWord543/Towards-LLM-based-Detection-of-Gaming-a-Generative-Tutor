import csv
import re

def sort_csv_by_filename(filepath):
    """Sort CSV rows numerically by the number in the Filename column."""

    # Read the CSV file
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Sort rows by extracting the number from the filename (e.g., "713.json" -> 713)
    def get_number(row):
        if row and row[0]:
            match = re.match(r'(\d+)', row[0])
            if match:
                return int(match.group(1))
        return float('inf')  # Put rows without valid numbers at the end

    sorted_rows = sorted(rows, key=get_number)

    # Write back to the same file
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(sorted_rows)

    print(f"Sorted {filepath} - {len(sorted_rows)} rows")

# Process all four CSV files
files = ['Run1.csv', 'Run2.csv', 'Run3.csv', 'Run4.csv', 'Run5.csv', 'Run6.csv', 'Run7.csv', 'Run8.csv', 'Run9.csv', 'Run10.csv']

for filename in files:
    sort_csv_by_filename(filename)

print("\nAll files sorted successfully!")
