import csv
from collections import defaultdict

def check_duplicates():
    """Check for duplicate filenames across all run CSV files."""

    files = ['Run1.csv', 'Run2.csv', 'Run3.csv', 'Run4.csv', 'Run5.csv',
             'Run6.csv', 'Run7.csv', 'Run8.csv', 'Run9.csv', 'Run10.csv']

    # Track which files each filename appears in
    filename_locations = defaultdict(list)

    for run_file in files:
        try:
            with open(run_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)
                for row in reader:
                    if row and row[0]:
                        filename = row[0]
                        filename_locations[filename].append(run_file)
        except FileNotFoundError:
            print(f"Warning: {run_file} not found")

    # Find duplicates (filenames appearing in more than one run)
    duplicates = {fname: locations for fname, locations in filename_locations.items()
                  if len(locations) > 1}

    if duplicates:
        print(f"Found {len(duplicates)} duplicate filename(s):\n")
        for filename, locations in sorted(duplicates.items()):
            print(f"  {filename} appears in: {', '.join(locations)}")
    else:
        print("No duplicates found across run files.")

    print(f"\nTotal unique filenames: {len(filename_locations)}")

if __name__ == "__main__":
    check_duplicates()
