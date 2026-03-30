#!/bin/bash

# Script to check if every file in checked folder appears in classifications CSVs

echo "=== Classification Coverage Check ==="
echo ""

# Get all files in checked folder
checked_files=$(ls -1 checked/ 2>/dev/null | sort)
checked_count=$(echo "$checked_files" | wc -l)

# Get unique filenames from classifications.csv (skip header, strip " - Round X" suffix)
if [ -f classifications.csv ]; then
    class1_files=$(tail -n +2 classifications.csv | cut -d',' -f1 | sed 's/ - Round [0-9]*$//' | sort -u)
    class1_count=$(echo "$class1_files" | grep -v '^$' | wc -l)
else
    class1_files=""
    class1_count=0
fi

# Get unique filenames from classifications2.csv (skip header, strip " - Round X" suffix)
if [ -f classifications2.csv ]; then
    class2_files=$(tail -n +2 classifications2.csv | cut -d',' -f1 | sed 's/ - Round [0-9]*$//' | sort -u)
    class2_count=$(echo "$class2_files" | grep -v '^$' | wc -l)
else
    class2_files=""
    class2_count=0
fi

echo "Files in checked folder: $checked_count"
echo "Unique files in classifications.csv: $class1_count"
echo "Unique files in classifications2.csv: $class2_count"
echo ""

# Combine both classification files
all_classified=$(echo -e "$class1_files\n$class2_files" | sort -u | grep -v '^$')
all_classified_count=$(echo "$all_classified" | wc -l)
echo "Total unique files in both CSVs: $all_classified_count"
echo ""

# Check each file in checked folder
missing_files=()
found_in_class1=0
found_in_class2=0
found_in_both=0
not_found=0

while IFS= read -r file; do
    if [ -z "$file" ]; then
        continue
    fi

    in_class1=false
    in_class2=false

    # Check if in classifications.csv
    if echo "$class1_files" | grep -Fxq "$file"; then
        in_class1=true
        ((found_in_class1++))
    fi

    # Check if in classifications2.csv
    if echo "$class2_files" | grep -Fxq "$file"; then
        in_class2=true
        ((found_in_class2++))
    fi

    # Check if in both
    if [ "$in_class1" = true ] && [ "$in_class2" = true ]; then
        ((found_in_both++))
        echo "WARNING: $file appears in BOTH classification files"
    fi

    # Check if in neither
    if [ "$in_class1" = false ] && [ "$in_class2" = false ]; then
        missing_files+=("$file")
        ((not_found++))
    fi
done <<< "$checked_files"

echo "=== Results ==="
echo "Files found only in classifications.csv: $((found_in_class1 - found_in_both))"
echo "Files found only in classifications2.csv: $((found_in_class2 - found_in_both))"
echo "Files found in BOTH CSVs: $found_in_both"
echo "Files NOT found in any CSV: $not_found"
echo ""

if [ $not_found -gt 0 ]; then
    echo "=== Missing Files (in checked/ but not in any CSV) ==="
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
fi

# Check for files in CSV but not in checked folder
echo "=== Checking for files in CSVs but not in checked folder ==="
csv_not_in_checked=0

while IFS= read -r file; do
    if [ -z "$file" ]; then
        continue
    fi

    if ! echo "$checked_files" | grep -Fxq "$file"; then
        echo "  - $file (in CSV but not in checked/)"
        ((csv_not_in_checked++))
    fi
done <<< "$all_classified"

if [ $csv_not_in_checked -eq 0 ]; then
    echo "  None - all classified files are in checked folder"
fi

echo ""
echo "=== Summary ==="
if [ $not_found -eq 0 ] && [ $found_in_both -eq 0 ]; then
    echo "✓ SUCCESS: All files in checked/ appear in exactly one CSV"
elif [ $not_found -eq 0 ]; then
    echo "⚠ WARNING: All files classified, but $found_in_both files appear in both CSVs"
else
    echo "✗ FAILURE: $not_found files in checked/ are missing from CSVs"
fi
