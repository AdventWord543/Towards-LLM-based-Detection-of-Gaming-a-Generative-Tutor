import csv
from collections import OrderedDict

input_file = "merged_classifications.csv"
output_file = "filename_gaming.csv"

# Use OrderedDict to preserve order of first appearance
filename_gaming = OrderedDict()

with open(input_file, "r", newline="", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)

    for row in reader:
        filename = row["Filename"]
        gaming = row["Gaming"]

        if filename not in filename_gaming:
            filename_gaming[filename] = []
        filename_gaming[filename].append(gaming)

# Find max number of gaming values for any filename
max_gaming = max(len(values) for values in filename_gaming.values())

# Write output
with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)

    # Header: Filename, Gaming1, Gaming2, etc.
    header = ["Filename"] + [f"Gaming{i+1}" for i in range(max_gaming)]
    writer.writerow(header)

    for filename, gaming_values in filename_gaming.items():
        row = [filename] + gaming_values
        writer.writerow(row)

print(f"Created {output_file} with {len(filename_gaming)} unique filenames.")
print(f"Max gaming values per filename: {max_gaming}")
