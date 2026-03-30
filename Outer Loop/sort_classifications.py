import csv
import re

def parse_filename(filename):
    """
    Parse filename like '07.3.4_C.txt' into sortable components.
    Returns (first_num, middle_num, final_num, suffix) or None if pattern doesn't match.
    """
    # Handle special cases like '17.3_B.txt' (only two numbers)
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)_([ABC])\.txt$', filename)
    if match:
        first = int(match.group(1))
        middle = int(match.group(2))
        final = int(match.group(3))
        suffix = match.group(4)
        return (first, middle, final, suffix)

    # Handle two-number format like '17.3_B.txt'
    # Treat the second number as "final" with middle=0, so suffix clusters correctly
    match = re.match(r'^(\d+)\.(\d+)_([ABC])\.txt$', filename)
    if match:
        first = int(match.group(1))
        middle = 0  # No middle number
        final = int(match.group(2))
        suffix = match.group(3)
        return (first, middle, final, suffix)

    return None

def sort_key(row):
    """
    Generate sort key for a row.
    Sort by: first number, middle number, suffix (A, B, C), then final number.
    This clusters all _A together, then _B, then _C within each XX.Y group.
    """
    filename = row[0]
    parsed = parse_filename(filename)

    if parsed:
        first, middle, final, suffix = parsed
        suffix_order = {'A': 0, 'B': 1, 'C': 2}
        return (first, middle, suffix_order.get(suffix, 3), final)
    else:
        # Put unparseable filenames at the end
        return (9999, 9999, 9999, 9999, filename)

def main():
    input_file = 'classifications.csv'
    output_file = 'classifications_sorted.csv'

    # Read the CSV
    with open(input_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    # Sort the rows
    rows.sort(key=sort_key)

    # Write the sorted CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print(f"Sorted {len(rows)} rows.")
    print(f"Output written to: {output_file}")

    # Show first 20 entries as preview
    print("\nFirst 20 entries:")
    for row in rows[:20]:
        print(f"  {row[0]}")

    # Show entries from 16-19 range to verify two-number format
    print("\nEntries starting with 16-19 (first 30):")
    count = 0
    for row in rows:
        if row[0].startswith(('16.', '17.', '18.', '19.')):
            print(f"  {row[0]}")
            count += 1
            if count >= 30:
                break

if __name__ == '__main__':
    main()
