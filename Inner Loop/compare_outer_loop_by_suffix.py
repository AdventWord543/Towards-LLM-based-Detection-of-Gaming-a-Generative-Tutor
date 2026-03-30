import pandas as pd
import numpy as np
import os

# Read the CSV files
truth_df = pd.read_csv('Outer Loop Truth.csv')
predicted_df = pd.read_csv('Outer Loop Predicted.csv')

# Rename columns for easier comparison
truth_df.columns = ['ID', 'Gaming_Truth', 'GCat_Truth', 'SCat_Truth']
predicted_df.columns = ['ID', 'Gaming_Pred', 'GCat_Pred', 'SCat_Pred']

# Merge the dataframes on ID
merged_df = pd.merge(truth_df, predicted_df, on='ID')

# Function to calculate accuracy
def calculate_accuracy(truth_col, pred_col):
    """Calculate accuracy between two columns, handling empty values"""
    valid_mask = (truth_col.notna() & (truth_col != '')) & (pred_col.notna() & (pred_col != ''))

    if valid_mask.sum() == 0:
        return 0.0, 0, 0

    matches = (truth_col[valid_mask] == pred_col[valid_mask]).sum()
    total = valid_mask.sum()
    accuracy = (matches / total) * 100 if total > 0 else 0

    return accuracy, matches, total

# Extract pattern information from ID
def extract_number(id_str):
    """Extract starting number (e.g., '01', '02', etc.)"""
    return id_str.split('.')[0]

def extract_pattern(id_str):
    """Extract pattern number (e.g., '.1.', '.2.', etc.)"""
    parts = id_str.split('.')
    if len(parts) >= 2:
        return f".{parts[1]}."
    return None

def extract_suffix(id_str):
    """Extract suffix (e.g., '_A', '_B', '_C')"""
    if '_' in id_str:
        return '_' + id_str.split('_')[-1]
    return None

merged_df['Number'] = merged_df['ID'].apply(extract_number)
merged_df['Pattern'] = merged_df['ID'].apply(extract_pattern)
merged_df['Suffix'] = merged_df['ID'].apply(extract_suffix)

# Create output directory
output_dir = 'Category_Reports_With_Suffix'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("=" * 80)
print("GENERATING DETAILED REPORTS WITH SUFFIX BREAKDOWN (_A, _B, _C)")
print("=" * 80)
print()

# Get all unique numbers and sort them
numbers = sorted(merged_df['Number'].unique())
suffixes = ['_A', '_B', '_C']

# Main summary report
summary_report = []
suffix_summary_report = []

# ===== GENERATE OVERALL SUFFIX ANALYSIS =====
overall_suffix_report = os.path.join(output_dir, 'Overall_Suffix_Analysis.txt')
with open(overall_suffix_report, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("OVERALL ANALYSIS BY SUFFIX (_A, _B, _C)\n")
    f.write("=" * 80 + "\n\n")

    for suffix in suffixes:
        suffix_df = merged_df[merged_df['Suffix'] == suffix]

        if len(suffix_df) > 0:
            gaming_acc, gaming_match, gaming_total = calculate_accuracy(
                suffix_df['Gaming_Truth'], suffix_df['Gaming_Pred'])
            gcat_acc, gcat_match, gcat_total = calculate_accuracy(
                suffix_df['GCat_Truth'], suffix_df['GCat_Pred'])
            scat_acc, scat_match, scat_total = calculate_accuracy(
                suffix_df['SCat_Truth'], suffix_df['SCat_Pred'])

            f.write(f"SUFFIX {suffix}:\n")
            f.write("-" * 80 + "\n")
            f.write(f"Gaming:        {gaming_acc:6.2f}% ({gaming_match}/{gaming_total} correct)\n")
            f.write(f"G Cat:         {gcat_acc:6.2f}% ({gcat_match}/{gcat_total} correct)\n")
            f.write(f"S Cat:         {scat_acc:6.2f}% ({scat_match}/{scat_total} correct)\n")
            f.write(f"Total items:   {len(suffix_df)}\n\n")

    # SCat mismatch analysis for overall data
    overall_scat_mismatches = merged_df[(merged_df['SCat_Truth'] != merged_df['SCat_Pred']) &
                                         (merged_df['SCat_Truth'].notna()) & (merged_df['SCat_Truth'] != '') &
                                         (merged_df['SCat_Pred'].notna()) & (merged_df['SCat_Pred'] != '')]

    # Also track overall cases where SCat_Truth is empty but SCat_Pred has a value
    overall_scat_empty_truth = merged_df[((merged_df['SCat_Truth'].isna()) | (merged_df['SCat_Truth'] == '')) &
                                          (merged_df['SCat_Pred'].notna()) & (merged_df['SCat_Pred'] != '')]

    # Empty truth analysis first
    if len(overall_scat_empty_truth) > 0:
        f.write("=" * 80 + "\n")
        f.write("OVERALL SCAT EMPTY TRUTH ANALYSIS - PREDICTIONS MADE WHEN TRUTH IS EMPTY\n")
        f.write("=" * 80 + "\n\n")

        # Count the predictions made when truth was empty
        empty_predictions = overall_scat_empty_truth['SCat_Pred'].value_counts()

        f.write(f"Total cases where SCat truth is empty but prediction was made: {len(overall_scat_empty_truth)}\n")
        f.write(f"Unique predictions made: {len(empty_predictions)}\n\n")
        f.write("Most common predictions when truth is empty (sorted by frequency):\n")
        f.write("-" * 80 + "\n")

        for pred, count in empty_predictions.items():
            percentage = (count / len(overall_scat_empty_truth)) * 100
            f.write(f"Empty -> {pred:<20} Count: {count:3d} ({percentage:5.1f}%)\n")

        f.write("\n")

        # Breakdown by category
        f.write("EMPTY TRUTH ANALYSIS BY CATEGORY:\n")
        f.write("-" * 80 + "\n")

        category_empty_counts = overall_scat_empty_truth['Number'].value_counts().sort_index()
        for category, count in category_empty_counts.items():
            percentage = (count / len(overall_scat_empty_truth)) * 100
            f.write(f"Category {category}: {count:3d} cases ({percentage:5.1f}%)\n")

        f.write("\n")

        # Breakdown by suffix
        f.write("EMPTY TRUTH ANALYSIS BY SUFFIX:\n")
        f.write("-" * 80 + "\n")

        for suffix in suffixes:
            suffix_empty = overall_scat_empty_truth[overall_scat_empty_truth['Suffix'] == suffix]

            if len(suffix_empty) > 0:
                f.write(f"\nSUFFIX {suffix} (Total empty truth cases: {len(suffix_empty)}):\n")

                suffix_empty_preds = suffix_empty['SCat_Pred'].value_counts()

                for pred, count in suffix_empty_preds.items():
                    percentage = (count / len(suffix_empty)) * 100
                    f.write(f"  Empty -> {pred:<18} Count: {count:3d} ({percentage:5.1f}%)\n")

        f.write("\n\n")

    if len(overall_scat_mismatches) > 0:
        f.write("=" * 80 + "\n")
        f.write("OVERALL SCAT MISMATCH ANALYSIS - MOST COMMON WRONG PREDICTIONS\n")
        f.write("=" * 80 + "\n\n")

        # Create a summary of Truth -> Predicted pairs
        mismatch_pairs = overall_scat_mismatches[['SCat_Truth', 'SCat_Pred']].copy()
        mismatch_pairs['Pair'] = mismatch_pairs.apply(
            lambda row: f"Truth: {row['SCat_Truth']:<15} -> Predicted: {row['SCat_Pred']}", axis=1
        )

        pair_counts = mismatch_pairs['Pair'].value_counts()

        f.write(f"Total SCat mismatches across all categories: {len(overall_scat_mismatches)}\n")
        f.write(f"Unique wrong prediction patterns: {len(pair_counts)}\n\n")
        f.write("Most common wrong predictions (sorted by frequency):\n")
        f.write("-" * 80 + "\n")

        for pair, count in pair_counts.items():
            percentage = (count / len(overall_scat_mismatches)) * 100
            f.write(f"{pair:<60} Count: {count:3d} ({percentage:5.1f}%)\n")

        f.write("\n")

        # Breakdown by suffix
        f.write("SCAT MISMATCH ANALYSIS BY SUFFIX:\n")
        f.write("-" * 80 + "\n")

        for suffix in suffixes:
            suffix_scat = overall_scat_mismatches[overall_scat_mismatches['Suffix'] == suffix]

            if len(suffix_scat) > 0:
                f.write(f"\nSUFFIX {suffix} (Total SCat mismatches: {len(suffix_scat)}):\n")

                suffix_pairs = suffix_scat[['SCat_Truth', 'SCat_Pred']].copy()
                suffix_pairs['Pair'] = suffix_pairs.apply(
                    lambda row: f"Truth: {row['SCat_Truth']:<15} -> Predicted: {row['SCat_Pred']}", axis=1
                )

                suffix_pair_counts = suffix_pairs['Pair'].value_counts()

                for pair, count in suffix_pair_counts.items():
                    percentage = (count / len(suffix_scat)) * 100
                    f.write(f"  {pair:<58} Count: {count:3d} ({percentage:5.1f}%)\n")

        f.write("\n\n")

    # Breakdown by suffix and pattern
    f.write("=" * 80 + "\n")
    f.write("SUFFIX BREAKDOWN BY PATTERN\n")
    f.write("=" * 80 + "\n\n")

    for suffix in suffixes:
        f.write(f"SUFFIX {suffix}:\n")
        f.write("-" * 80 + "\n")

        patterns = ['.1.', '.2.', '.3.', '.4.']
        for pattern in patterns:
            pattern_suffix_df = merged_df[(merged_df['Suffix'] == suffix) &
                                          (merged_df['Pattern'] == pattern)]

            if len(pattern_suffix_df) > 0:
                gaming_acc, gaming_match, gaming_total = calculate_accuracy(
                    pattern_suffix_df['Gaming_Truth'], pattern_suffix_df['Gaming_Pred'])
                gcat_acc, gcat_match, gcat_total = calculate_accuracy(
                    pattern_suffix_df['GCat_Truth'], pattern_suffix_df['GCat_Pred'])
                scat_acc, scat_match, scat_total = calculate_accuracy(
                    pattern_suffix_df['SCat_Truth'], pattern_suffix_df['SCat_Pred'])

                f.write(f"  Pattern {pattern}:\n")
                f.write(f"    Gaming:        {gaming_acc:6.2f}% ({gaming_match}/{gaming_total})\n")
                f.write(f"    G Cat:         {gcat_acc:6.2f}% ({gcat_match}/{gcat_total})\n")
                f.write(f"    S Cat:         {scat_acc:6.2f}% ({scat_match}/{scat_total})\n")
        f.write("\n")

print(f"[OK] Created overall suffix analysis: {overall_suffix_report}")

# Generate individual reports for each number
for num in numbers:
    num_df = merged_df[merged_df['Number'] == num]

    # Create report filename
    report_filename = os.path.join(output_dir, f'Category_{num}_Full_Report.txt')

    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"DETAILED ACCURACY REPORT FOR CATEGORY {num}\n")
        f.write("=" * 80 + "\n\n")

        # Overall accuracy for this category
        gaming_acc, gaming_match, gaming_total = calculate_accuracy(num_df['Gaming_Truth'], num_df['Gaming_Pred'])
        gcat_acc, gcat_match, gcat_total = calculate_accuracy(num_df['GCat_Truth'], num_df['GCat_Pred'])
        scat_acc, scat_match, scat_total = calculate_accuracy(num_df['SCat_Truth'], num_df['SCat_Pred'])

        f.write("OVERALL ACCURACY FOR CATEGORY " + num + ":\n")
        f.write("-" * 80 + "\n")
        f.write(f"Gaming:        {gaming_acc:6.2f}% ({gaming_match}/{gaming_total} correct)\n")
        f.write(f"G Cat:         {gcat_acc:6.2f}% ({gcat_match}/{gcat_total} correct)\n")
        f.write(f"S Cat:         {scat_acc:6.2f}% ({scat_match}/{scat_total} correct)\n\n")

        # Store for summary
        summary_report.append({
            'Category': num,
            'Gaming_Acc': gaming_acc,
            'Gaming_Match': f"{gaming_match}/{gaming_total}",
            'GCat_Acc': gcat_acc,
            'GCat_Match': f"{gcat_match}/{gcat_total}",
            'SCat_Acc': scat_acc,
            'SCat_Match': f"{scat_match}/{scat_total}"
        })

        # ===== NEW: BREAKDOWN BY SUFFIX =====
        f.write("BREAKDOWN BY SUFFIX (_A, _B, _C):\n")
        f.write("=" * 80 + "\n")

        for suffix in suffixes:
            suffix_df = num_df[num_df['Suffix'] == suffix]

            if len(suffix_df) > 0:
                s_gaming_acc, s_gaming_match, s_gaming_total = calculate_accuracy(
                    suffix_df['Gaming_Truth'], suffix_df['Gaming_Pred'])
                s_gcat_acc, s_gcat_match, s_gcat_total = calculate_accuracy(
                    suffix_df['GCat_Truth'], suffix_df['GCat_Pred'])
                s_scat_acc, s_scat_match, s_scat_total = calculate_accuracy(
                    suffix_df['SCat_Truth'], suffix_df['SCat_Pred'])

                f.write(f"\nSuffix {suffix}:\n")
                f.write(f"  Gaming:        {s_gaming_acc:6.2f}% ({s_gaming_match}/{s_gaming_total})\n")
                f.write(f"  G Cat:         {s_gcat_acc:6.2f}% ({s_gcat_match}/{s_gcat_total})\n")
                f.write(f"  S Cat:         {s_scat_acc:6.2f}% ({s_scat_match}/{s_scat_total})\n")

                # Store suffix summary
                suffix_summary_report.append({
                    'Category': num,
                    'Suffix': suffix,
                    'Gaming_Acc': s_gaming_acc,
                    'Gaming_Match': f"{s_gaming_match}/{s_gaming_total}",
                    'GCat_Acc': s_gcat_acc,
                    'GCat_Match': f"{s_gcat_match}/{s_gcat_total}",
                    'SCat_Acc': s_scat_acc,
                    'SCat_Match': f"{s_scat_match}/{s_scat_total}"
                })

        f.write("\n")

        # Breakdown by pattern
        f.write("BREAKDOWN BY PATTERN:\n")
        f.write("-" * 80 + "\n")
        patterns = ['.1.', '.2.', '.3.', '.4.']

        for pattern in patterns:
            pattern_df = num_df[num_df['Pattern'] == pattern]

            if len(pattern_df) > 0:
                p_gaming_acc, p_gaming_match, p_gaming_total = calculate_accuracy(
                    pattern_df['Gaming_Truth'], pattern_df['Gaming_Pred'])
                p_gcat_acc, p_gcat_match, p_gcat_total = calculate_accuracy(
                    pattern_df['GCat_Truth'], pattern_df['GCat_Pred'])
                p_scat_acc, p_scat_match, p_scat_total = calculate_accuracy(
                    pattern_df['SCat_Truth'], pattern_df['SCat_Pred'])

                f.write(f"\nPattern {pattern}:\n")
                f.write(f"  Gaming:        {p_gaming_acc:6.2f}% ({p_gaming_match}/{p_gaming_total})\n")
                f.write(f"  G Cat:         {p_gcat_acc:6.2f}% ({p_gcat_match}/{p_gcat_total})\n")
                f.write(f"  S Cat:         {p_scat_acc:6.2f}% ({p_scat_match}/{p_scat_total})\n")

        f.write("\n")

        # ===== NEW: BREAKDOWN BY PATTERN AND SUFFIX COMBINED =====
        f.write("BREAKDOWN BY PATTERN AND SUFFIX COMBINED:\n")
        f.write("=" * 80 + "\n")

        for pattern in patterns:
            f.write(f"\nPattern {pattern}:\n")
            f.write("-" * 40 + "\n")

            for suffix in suffixes:
                ps_df = num_df[(num_df['Pattern'] == pattern) & (num_df['Suffix'] == suffix)]

                if len(ps_df) > 0:
                    ps_gaming_acc, ps_gaming_match, ps_gaming_total = calculate_accuracy(
                        ps_df['Gaming_Truth'], ps_df['Gaming_Pred'])
                    ps_gcat_acc, ps_gcat_match, ps_gcat_total = calculate_accuracy(
                        ps_df['GCat_Truth'], ps_df['GCat_Pred'])
                    ps_scat_acc, ps_scat_match, ps_scat_total = calculate_accuracy(
                        ps_df['SCat_Truth'], ps_df['SCat_Pred'])

                    f.write(f"  {suffix}: Gaming {ps_gaming_acc:6.2f}% ({ps_gaming_match}/{ps_gaming_total}), ")
                    f.write(f"G Cat {ps_gcat_acc:6.2f}% ({ps_gcat_match}/{ps_gcat_total}), ")
                    f.write(f"S Cat {ps_scat_acc:6.2f}% ({ps_scat_match}/{ps_scat_total})\n")

        f.write("\n")

        # Detailed comparison table (grouped by suffix)
        f.write("DETAILED ITEM-BY-ITEM COMPARISON (GROUPED BY SUFFIX):\n")
        f.write("=" * 80 + "\n")

        for suffix in suffixes:
            suffix_df = num_df[num_df['Suffix'] == suffix]

            if len(suffix_df) > 0:
                f.write(f"\nSUFFIX {suffix}:\n")
                f.write(f"{'ID':<15} {'Gaming':<8} {'GCat':<12} {'SCat':<15} {'Status':<10}\n")
                f.write(f"{'':<15} {'T|P':<8} {'Truth|Pred':<12} {'Truth|Pred':<15}\n")
                f.write("-" * 80 + "\n")

                for _, row in suffix_df.iterrows():
                    gaming_match = 'Y' if row['Gaming_Truth'] == row['Gaming_Pred'] else 'N'
                    gcat_match = 'Y' if row['GCat_Truth'] == row['GCat_Pred'] else 'N'
                    scat_match = 'Y' if row['SCat_Truth'] == row['SCat_Pred'] else 'N'

                    # Handle empty values
                    gt = row['Gaming_Truth'] if pd.notna(row['Gaming_Truth']) and row['Gaming_Truth'] != '' else '-'
                    gp = row['Gaming_Pred'] if pd.notna(row['Gaming_Pred']) and row['Gaming_Pred'] != '' else '-'
                    gct = row['GCat_Truth'] if pd.notna(row['GCat_Truth']) and row['GCat_Truth'] != '' else '-'
                    gcp = row['GCat_Pred'] if pd.notna(row['GCat_Pred']) and row['GCat_Pred'] != '' else '-'
                    sct = row['SCat_Truth'] if pd.notna(row['SCat_Truth']) and row['SCat_Truth'] != '' else '-'
                    scp = row['SCat_Pred'] if pd.notna(row['SCat_Pred']) and row['SCat_Pred'] != '' else '-'

                    # Skip comparison if both are empty
                    if gt == '-' and gp == '-':
                        gaming_match = '-'
                    if gct == '-' and gcp == '-':
                        gcat_match = '-'
                    if sct == '-' and scp == '-':
                        scat_match = '-'

                    overall_status = 'PERFECT' if (gaming_match == 'Y' and gcat_match == 'Y' and scat_match == 'Y') else 'MISMATCH'
                    if gaming_match == '-' and gcat_match == '-' and scat_match == '-':
                        overall_status = 'EMPTY'

                    f.write(f"{row['ID']:<15} {gt[:3]}/{gp[:3]:<8} ")
                    f.write(f"{gct[:5]}/{gcp[:5]:<12} ")
                    f.write(f"{sct[:7]}/{scp[:7]:<15} ")
                    f.write(f"{gaming_match}{gcat_match}{scat_match} {overall_status}\n")

        f.write("\n")

        # Mismatches summary
        gaming_mismatches = num_df[(num_df['Gaming_Truth'] != num_df['Gaming_Pred']) &
                                   (num_df['Gaming_Truth'].notna()) & (num_df['Gaming_Truth'] != '') &
                                   (num_df['Gaming_Pred'].notna()) & (num_df['Gaming_Pred'] != '')]

        gcat_mismatches = num_df[(num_df['GCat_Truth'] != num_df['GCat_Pred']) &
                                 (num_df['GCat_Truth'].notna()) & (num_df['GCat_Truth'] != '') &
                                 (num_df['GCat_Pred'].notna()) & (num_df['GCat_Pred'] != '')]

        scat_mismatches = num_df[(num_df['SCat_Truth'] != num_df['SCat_Pred']) &
                                 (num_df['SCat_Truth'].notna()) & (num_df['SCat_Truth'] != '') &
                                 (num_df['SCat_Pred'].notna()) & (num_df['SCat_Pred'] != '')]

        # Also track cases where SCat_Truth is empty but SCat_Pred has a value
        scat_empty_truth_mismatches = num_df[((num_df['SCat_Truth'].isna()) | (num_df['SCat_Truth'] == '')) &
                                               (num_df['SCat_Pred'].notna()) & (num_df['SCat_Pred'] != '')]

        f.write("MISMATCH SUMMARY:\n")
        f.write("=" * 80 + "\n")
        f.write(f"Gaming mismatches: {len(gaming_mismatches)}\n")
        f.write(f"G Cat mismatches:  {len(gcat_mismatches)}\n")
        f.write(f"S Cat mismatches:  {len(scat_mismatches)}\n")
        f.write(f"S Cat empty truth with predictions: {len(scat_empty_truth_mismatches)}\n\n")

        # Mismatch breakdown by suffix
        f.write("MISMATCH BREAKDOWN BY SUFFIX:\n")
        f.write("-" * 80 + "\n")
        for suffix in suffixes:
            suffix_gaming = gaming_mismatches[gaming_mismatches['Suffix'] == suffix]
            suffix_gcat = gcat_mismatches[gcat_mismatches['Suffix'] == suffix]
            suffix_scat = scat_mismatches[scat_mismatches['Suffix'] == suffix]
            suffix_scat_empty = scat_empty_truth_mismatches[scat_empty_truth_mismatches['Suffix'] == suffix]

            f.write(f"{suffix}: Gaming={len(suffix_gaming)}, G Cat={len(suffix_gcat)}, S Cat={len(suffix_scat)}, S Cat Empty→Pred={len(suffix_scat_empty)}\n")

        f.write("\n")

        # SCat empty truth analysis - predictions made when truth is empty
        if len(scat_empty_truth_mismatches) > 0:
            f.write("SCAT EMPTY TRUTH ANALYSIS - PREDICTIONS MADE WHEN TRUTH IS EMPTY:\n")
            f.write("=" * 80 + "\n")

            # Count the predictions made when truth was empty
            empty_predictions = scat_empty_truth_mismatches['SCat_Pred'].value_counts()

            f.write(f"Total cases where SCat truth is empty but prediction was made: {len(scat_empty_truth_mismatches)}\n")
            f.write(f"Unique predictions made: {len(empty_predictions)}\n\n")
            f.write("Most common predictions when truth is empty (sorted by frequency):\n")
            f.write("-" * 80 + "\n")

            for pred, count in empty_predictions.items():
                percentage = (count / len(scat_empty_truth_mismatches)) * 100
                f.write(f"Empty -> {pred:<20} Count: {count:3d} ({percentage:5.1f}%)\n")

            f.write("\n")

            # Breakdown by suffix
            f.write("EMPTY TRUTH ANALYSIS BY SUFFIX:\n")
            f.write("-" * 80 + "\n")

            for suffix in suffixes:
                suffix_empty = scat_empty_truth_mismatches[scat_empty_truth_mismatches['Suffix'] == suffix]

                if len(suffix_empty) > 0:
                    f.write(f"\nSUFFIX {suffix} (Total empty truth cases: {len(suffix_empty)}):\n")

                    suffix_empty_preds = suffix_empty['SCat_Pred'].value_counts()

                    for pred, count in suffix_empty_preds.items():
                        percentage = (count / len(suffix_empty)) * 100
                        f.write(f"  Empty -> {pred:<18} Count: {count:3d} ({percentage:5.1f}%)\n")

            f.write("\n\n")

        # SCat mismatch analysis - most common wrong predictions
        if len(scat_mismatches) > 0:
            f.write("SCAT MISMATCH ANALYSIS - MOST COMMON WRONG PREDICTIONS:\n")
            f.write("=" * 80 + "\n")

            # Create a summary of Truth -> Predicted pairs
            mismatch_pairs = scat_mismatches[['SCat_Truth', 'SCat_Pred']].copy()
            mismatch_pairs['Pair'] = mismatch_pairs.apply(
                lambda row: f"Truth: {row['SCat_Truth']:<15} -> Predicted: {row['SCat_Pred']}", axis=1
            )

            pair_counts = mismatch_pairs['Pair'].value_counts()

            f.write(f"Total SCat mismatches: {len(scat_mismatches)}\n")
            f.write(f"Unique wrong prediction patterns: {len(pair_counts)}\n\n")
            f.write("Most common wrong predictions (sorted by frequency):\n")
            f.write("-" * 80 + "\n")

            for pair, count in pair_counts.items():
                percentage = (count / len(scat_mismatches)) * 100
                f.write(f"{pair:<60} Count: {count:3d} ({percentage:5.1f}%)\n")

            f.write("\n")

            # Breakdown by suffix
            f.write("SCAT MISMATCH ANALYSIS BY SUFFIX:\n")
            f.write("-" * 80 + "\n")

            for suffix in suffixes:
                suffix_scat = scat_mismatches[scat_mismatches['Suffix'] == suffix]

                if len(suffix_scat) > 0:
                    f.write(f"\nSUFFIX {suffix} (Total SCat mismatches: {len(suffix_scat)}):\n")

                    suffix_pairs = suffix_scat[['SCat_Truth', 'SCat_Pred']].copy()
                    suffix_pairs['Pair'] = suffix_pairs.apply(
                        lambda row: f"Truth: {row['SCat_Truth']:<15} -> Predicted: {row['SCat_Pred']}", axis=1
                    )

                    suffix_pair_counts = suffix_pairs['Pair'].value_counts()

                    for pair, count in suffix_pair_counts.items():
                        percentage = (count / len(suffix_scat)) * 100
                        f.write(f"  {pair:<58} Count: {count:3d} ({percentage:5.1f}%)\n")

            f.write("\n")

        f.write("\n")

    print(f"[OK] Created report for Category {num}: {report_filename}")

    # ===== CREATE SEPARATE REPORTS FOR EACH CATEGORY-SUFFIX COMBINATION =====
    for suffix in suffixes:
        suffix_num_df = num_df[num_df['Suffix'] == suffix]

        if len(suffix_num_df) > 0:
            suffix_report_filename = os.path.join(output_dir, f'Category_{num}{suffix}_Report.txt')

            with open(suffix_report_filename, 'w', encoding='utf-8') as sf:
                sf.write("=" * 80 + "\n")
                sf.write(f"DETAILED REPORT FOR CATEGORY {num}{suffix}\n")
                sf.write("=" * 80 + "\n\n")

                # Accuracy for this category-suffix combination
                s_gaming_acc, s_gaming_match, s_gaming_total = calculate_accuracy(
                    suffix_num_df['Gaming_Truth'], suffix_num_df['Gaming_Pred'])
                s_gcat_acc, s_gcat_match, s_gcat_total = calculate_accuracy(
                    suffix_num_df['GCat_Truth'], suffix_num_df['GCat_Pred'])
                s_scat_acc, s_scat_match, s_scat_total = calculate_accuracy(
                    suffix_num_df['SCat_Truth'], suffix_num_df['SCat_Pred'])

                sf.write(f"ACCURACY FOR {num}{suffix}:\n")
                sf.write("-" * 80 + "\n")
                sf.write(f"Gaming:        {s_gaming_acc:6.2f}% ({s_gaming_match}/{s_gaming_total} correct)\n")
                sf.write(f"G Cat:         {s_gcat_acc:6.2f}% ({s_gcat_match}/{s_gcat_total} correct)\n")
                sf.write(f"S Cat:         {s_scat_acc:6.2f}% ({s_scat_match}/{s_scat_total} correct)\n\n")

                # Pattern breakdown for this suffix
                sf.write("BREAKDOWN BY PATTERN:\n")
                sf.write("-" * 80 + "\n")

                for pattern in ['.1.', '.2.', '.3.', '.4.']:
                    ps_df = suffix_num_df[suffix_num_df['Pattern'] == pattern]

                    if len(ps_df) > 0:
                        ps_gaming_acc, ps_gaming_match, ps_gaming_total = calculate_accuracy(
                            ps_df['Gaming_Truth'], ps_df['Gaming_Pred'])
                        ps_gcat_acc, ps_gcat_match, ps_gcat_total = calculate_accuracy(
                            ps_df['GCat_Truth'], ps_df['GCat_Pred'])
                        ps_scat_acc, ps_scat_match, ps_scat_total = calculate_accuracy(
                            ps_df['SCat_Truth'], ps_df['SCat_Pred'])

                        sf.write(f"\nPattern {pattern}:\n")
                        sf.write(f"  Gaming:        {ps_gaming_acc:6.2f}% ({ps_gaming_match}/{ps_gaming_total})\n")
                        sf.write(f"  G Cat:         {ps_gcat_acc:6.2f}% ({ps_gcat_match}/{ps_gcat_total})\n")
                        sf.write(f"  S Cat:         {ps_scat_acc:6.2f}% ({ps_scat_match}/{ps_scat_total})\n")

                sf.write("\n")

                # Item-by-item for this suffix
                sf.write("ITEM-BY-ITEM COMPARISON:\n")
                sf.write("=" * 80 + "\n")
                sf.write(f"{'ID':<15} {'Gaming':<8} {'GCat':<12} {'SCat':<15} {'Status':<10}\n")
                sf.write(f"{'':<15} {'T|P':<8} {'Truth|Pred':<12} {'Truth|Pred':<15}\n")
                sf.write("-" * 80 + "\n")

                for _, row in suffix_num_df.iterrows():
                    gaming_match = 'Y' if row['Gaming_Truth'] == row['Gaming_Pred'] else 'N'
                    gcat_match = 'Y' if row['GCat_Truth'] == row['GCat_Pred'] else 'N'
                    scat_match = 'Y' if row['SCat_Truth'] == row['SCat_Pred'] else 'N'

                    gt = row['Gaming_Truth'] if pd.notna(row['Gaming_Truth']) and row['Gaming_Truth'] != '' else '-'
                    gp = row['Gaming_Pred'] if pd.notna(row['Gaming_Pred']) and row['Gaming_Pred'] != '' else '-'
                    gct = row['GCat_Truth'] if pd.notna(row['GCat_Truth']) and row['GCat_Truth'] != '' else '-'
                    gcp = row['GCat_Pred'] if pd.notna(row['GCat_Pred']) and row['GCat_Pred'] != '' else '-'
                    sct = row['SCat_Truth'] if pd.notna(row['SCat_Truth']) and row['SCat_Truth'] != '' else '-'
                    scp = row['SCat_Pred'] if pd.notna(row['SCat_Pred']) and row['SCat_Pred'] != '' else '-'

                    if gt == '-' and gp == '-':
                        gaming_match = '-'
                    if gct == '-' and gcp == '-':
                        gcat_match = '-'
                    if sct == '-' and scp == '-':
                        scat_match = '-'

                    overall_status = 'PERFECT' if (gaming_match == 'Y' and gcat_match == 'Y' and scat_match == 'Y') else 'MISMATCH'
                    if gaming_match == '-' and gcat_match == '-' and scat_match == '-':
                        overall_status = 'EMPTY'

                    sf.write(f"{row['ID']:<15} {gt[:3]}/{gp[:3]:<8} ")
                    sf.write(f"{gct[:5]}/{gcp[:5]:<12} ")
                    sf.write(f"{sct[:7]}/{scp[:7]:<15} ")
                    sf.write(f"{gaming_match}{gcat_match}{scat_match} {overall_status}\n")

            print(f"[OK] Created report for {num}{suffix}: {suffix_report_filename}")

# Create summary CSV
summary_df = pd.DataFrame(summary_report)
summary_csv = os.path.join(output_dir, 'Summary_All_Categories.csv')
summary_df.to_csv(summary_csv, index=False)
print(f"\n[OK] Created summary CSV: {summary_csv}")

# Create suffix summary CSV
suffix_summary_df = pd.DataFrame(suffix_summary_report)
suffix_summary_csv = os.path.join(output_dir, 'Summary_By_Suffix.csv')
suffix_summary_df.to_csv(suffix_summary_csv, index=False)
print(f"[OK] Created suffix summary CSV: {suffix_summary_csv}")

# Create master summary report
master_report = os.path.join(output_dir, 'Master_Summary_Report.txt')
with open(master_report, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("MASTER SUMMARY REPORT - ALL CATEGORIES WITH SUFFIX BREAKDOWN\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"{'Category':<10} {'Gaming Acc':<15} {'G Cat Acc':<15} {'S Cat Acc':<15}\n")
    f.write("-" * 80 + "\n")

    for item in summary_report:
        f.write(f"{item['Category']:<10} ")
        f.write(f"{item['Gaming_Acc']:6.2f}% ({item['Gaming_Match']:<6}) ")
        f.write(f"{item['GCat_Acc']:6.2f}% ({item['GCat_Match']:<6}) ")
        f.write(f"{item['SCat_Acc']:6.2f}% ({item['SCat_Match']:<6})\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("BREAKDOWN BY SUFFIX\n")
    f.write("=" * 80 + "\n\n")

    for suffix in suffixes:
        suffix_df = merged_df[merged_df['Suffix'] == suffix]

        if len(suffix_df) > 0:
            gaming_acc, gaming_match, gaming_total = calculate_accuracy(
                suffix_df['Gaming_Truth'], suffix_df['Gaming_Pred'])
            gcat_acc, gcat_match, gcat_total = calculate_accuracy(
                suffix_df['GCat_Truth'], suffix_df['GCat_Pred'])
            scat_acc, scat_match, scat_total = calculate_accuracy(
                suffix_df['SCat_Truth'], suffix_df['SCat_Pred'])

            f.write(f"ALL {suffix} files:\n")
            f.write(f"  Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n")
            f.write(f"  G Cat:         {gcat_acc:.2f}% ({gcat_match}/{gcat_total})\n")
            f.write(f"  S Cat:         {scat_acc:.2f}% ({scat_match}/{scat_total})\n\n")

    f.write("=" * 80 + "\n")
    f.write("OVERALL STATISTICS\n")
    f.write("=" * 80 + "\n\n")

    gaming_acc, gaming_match, gaming_total = calculate_accuracy(merged_df['Gaming_Truth'], merged_df['Gaming_Pred'])
    gcat_acc, gcat_match, gcat_total = calculate_accuracy(merged_df['GCat_Truth'], merged_df['GCat_Pred'])
    scat_acc, scat_match, scat_total = calculate_accuracy(merged_df['SCat_Truth'], merged_df['SCat_Pred'])

    f.write(f"Overall Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n")
    f.write(f"Overall G Cat:         {gcat_acc:.2f}% ({gcat_match}/{gcat_total})\n")
    f.write(f"Overall S Cat:         {scat_acc:.2f}% ({scat_match}/{scat_total})\n\n")

    f.write("Range 01-14:\n")
    range_01_14 = merged_df[merged_df['Number'].isin([f'{i:02d}' for i in range(1, 15)])]
    gaming_acc, gaming_match, gaming_total = calculate_accuracy(range_01_14['Gaming_Truth'], range_01_14['Gaming_Pred'])
    gcat_acc, gcat_match, gcat_total = calculate_accuracy(range_01_14['GCat_Truth'], range_01_14['GCat_Pred'])
    scat_acc, scat_match, scat_total = calculate_accuracy(range_01_14['SCat_Truth'], range_01_14['SCat_Pred'])
    f.write(f"  Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n")
    f.write(f"  G Cat:         {gcat_acc:.2f}% ({gcat_match}/{gcat_total})\n")
    f.write(f"  S Cat:         {scat_acc:.2f}% ({scat_match}/{scat_total})\n\n")

    f.write("Range 16-19:\n")
    range_16_19 = merged_df[merged_df['Number'].isin([f'{i:02d}' for i in range(16, 20)])]
    gaming_acc, gaming_match, gaming_total = calculate_accuracy(range_16_19['Gaming_Truth'], range_16_19['Gaming_Pred'])
    gcat_acc, gcat_match, gcat_total = calculate_accuracy(range_16_19['GCat_Truth'], range_16_19['GCat_Pred'])
    scat_acc, scat_match, scat_total = calculate_accuracy(range_16_19['SCat_Truth'], range_16_19['SCat_Pred'])
    f.write(f"  Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n")
    f.write(f"  G Cat:         {gcat_acc:.2f}% ({gcat_match}/{gcat_total})\n")
    f.write(f"  S Cat:         {scat_acc:.2f}% ({scat_match}/{scat_total})\n\n")

    f.write("By Pattern:\n")
    patterns = ['.1.', '.2.', '.3.', '.4.']
    for pattern in patterns:
        pattern_df = merged_df[merged_df['Pattern'] == pattern]
        if len(pattern_df) > 0:
            gaming_acc, gaming_match, gaming_total = calculate_accuracy(pattern_df['Gaming_Truth'], pattern_df['Gaming_Pred'])
            gcat_acc, gcat_match, gcat_total = calculate_accuracy(pattern_df['GCat_Truth'], pattern_df['GCat_Pred'])
            scat_acc, scat_match, scat_total = calculate_accuracy(pattern_df['SCat_Truth'], pattern_df['SCat_Pred'])
            f.write(f"  Pattern {pattern}:\n")
            f.write(f"    Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n")
            f.write(f"    G Cat:         {gcat_acc:.2f}% ({gcat_match}/{gcat_total})\n")
            f.write(f"    S Cat:         {scat_acc:.2f}% ({scat_match}/{scat_total})\n")

print(f"[OK] Created master summary: {master_report}")

# ===== CREATE MISMATCH SUMMARY CSV =====
mismatch_summary_csv = os.path.join(output_dir, 'Mismatch_Summary.csv')

# Collect all GCat mismatches (including empty truth)
gcat_mismatch_data = []

# GCat: Regular mismatches (both have values but don't match)
gcat_mismatches = merged_df[(merged_df['GCat_Truth'] != merged_df['GCat_Pred']) &
                            (merged_df['GCat_Truth'].notna()) & (merged_df['GCat_Truth'] != '') &
                            (merged_df['GCat_Pred'].notna()) & (merged_df['GCat_Pred'] != '')]

for _, row in gcat_mismatches.iterrows():
    gcat_mismatch_data.append({
        'Category': 'GCat',
        'Truth': row['GCat_Truth'],
        'Predicted': row['GCat_Pred'],
        'ID': row['ID']
    })

# GCat: Empty truth but has prediction
gcat_empty_truth = merged_df[((merged_df['GCat_Truth'].isna()) | (merged_df['GCat_Truth'] == '')) &
                             (merged_df['GCat_Pred'].notna()) & (merged_df['GCat_Pred'] != '')]

for _, row in gcat_empty_truth.iterrows():
    gcat_mismatch_data.append({
        'Category': 'GCat',
        'Truth': '(empty)',
        'Predicted': row['GCat_Pred'],
        'ID': row['ID']
    })

# Collect all SCat mismatches (including empty truth)
scat_mismatch_data = []

# SCat: Regular mismatches (both have values but don't match)
scat_mismatches = merged_df[(merged_df['SCat_Truth'] != merged_df['SCat_Pred']) &
                            (merged_df['SCat_Truth'].notna()) & (merged_df['SCat_Truth'] != '') &
                            (merged_df['SCat_Pred'].notna()) & (merged_df['SCat_Pred'] != '')]

for _, row in scat_mismatches.iterrows():
    scat_mismatch_data.append({
        'Category': 'SCat',
        'Truth': row['SCat_Truth'],
        'Predicted': row['SCat_Pred'],
        'ID': row['ID']
    })

# SCat: Empty truth but has prediction
scat_empty_truth = merged_df[((merged_df['SCat_Truth'].isna()) | (merged_df['SCat_Truth'] == '')) &
                             (merged_df['SCat_Pred'].notna()) & (merged_df['SCat_Pred'] != '')]

for _, row in scat_empty_truth.iterrows():
    scat_mismatch_data.append({
        'Category': 'SCat',
        'Truth': '(empty)',
        'Predicted': row['SCat_Pred'],
        'ID': row['ID']
    })

# Combine all mismatches
all_mismatches = gcat_mismatch_data + scat_mismatch_data

# Create DataFrame and save
if len(all_mismatches) > 0:
    mismatch_df = pd.DataFrame(all_mismatches)
    mismatch_df.to_csv(mismatch_summary_csv, index=False)
    print(f"\n[OK] Created mismatch summary CSV: {mismatch_summary_csv}")
    print(f"     Total GCat mismatches: {len(gcat_mismatch_data)}")
    print(f"     Total SCat mismatches: {len(scat_mismatch_data)}")

    # Create a summary count CSV
    mismatch_counts_csv = os.path.join(output_dir, 'Mismatch_Counts_Summary.csv')

    # Count pairs for GCat
    gcat_pairs = []
    if len(gcat_mismatch_data) > 0:
        gcat_df = pd.DataFrame(gcat_mismatch_data)
        gcat_pair_counts = gcat_df.groupby(['Truth', 'Predicted']).size().reset_index(name='Count')
        gcat_pair_counts['Category'] = 'GCat'
        gcat_pair_counts = gcat_pair_counts.sort_values('Count', ascending=False)
        gcat_pairs = gcat_pair_counts.to_dict('records')

    # Count pairs for SCat
    scat_pairs = []
    if len(scat_mismatch_data) > 0:
        scat_df = pd.DataFrame(scat_mismatch_data)
        scat_pair_counts = scat_df.groupby(['Truth', 'Predicted']).size().reset_index(name='Count')
        scat_pair_counts['Category'] = 'SCat'
        scat_pair_counts = scat_pair_counts.sort_values('Count', ascending=False)
        scat_pairs = scat_pair_counts.to_dict('records')

    # Combine and save
    all_pairs = gcat_pairs + scat_pairs
    if len(all_pairs) > 0:
        pairs_df = pd.DataFrame(all_pairs)
        pairs_df = pairs_df[['Category', 'Truth', 'Predicted', 'Count']]
        pairs_df.to_csv(mismatch_counts_csv, index=False)
        print(f"[OK] Created mismatch counts summary CSV: {mismatch_counts_csv}")

    # Create a text summary report
    mismatch_text_report = os.path.join(output_dir, 'Mismatch_Summary_Report.txt')
    with open(mismatch_text_report, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("MISMATCH SUMMARY REPORT - GCAT AND SCAT MISCLASSIFICATIONS\n")
        f.write("=" * 80 + "\n\n")

        # Overall statistics
        f.write("OVERALL STATISTICS:\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total GCat mismatches: {len(gcat_mismatch_data)}\n")
        f.write(f"Total SCat mismatches: {len(scat_mismatch_data)}\n")
        f.write(f"Total mismatches:      {len(all_mismatches)}\n\n")

        # GCat analysis
        if len(gcat_mismatch_data) > 0:
            f.write("=" * 80 + "\n")
            f.write("GCAT MISMATCH ANALYSIS\n")
            f.write("=" * 80 + "\n\n")

            gcat_df = pd.DataFrame(gcat_mismatch_data)

            # Separate empty truth from regular mismatches
            gcat_empty = gcat_df[gcat_df['Truth'] == '(empty)']
            gcat_regular = gcat_df[gcat_df['Truth'] != '(empty)']

            # Regular mismatches
            if len(gcat_regular) > 0:
                f.write(f"Regular Mismatches (both truth and prediction have values): {len(gcat_regular)}\n")
                f.write("-" * 80 + "\n")

                gcat_regular_counts = gcat_regular.groupby(['Truth', 'Predicted']).size().reset_index(name='Count')
                gcat_regular_counts = gcat_regular_counts.sort_values('Count', ascending=False)

                f.write(f"{'Truth':<20} {'→':<3} {'Predicted':<20} {'Count':<10} {'%':<10}\n")
                f.write("-" * 80 + "\n")

                for _, row in gcat_regular_counts.iterrows():
                    percentage = (row['Count'] / len(gcat_regular)) * 100
                    f.write(f"{row['Truth']:<20} {'→':<3} {row['Predicted']:<20} {row['Count']:<10} {percentage:5.1f}%\n")

                f.write("\n")

            # Empty truth mismatches
            if len(gcat_empty) > 0:
                f.write(f"Empty Truth Mismatches (truth is empty but prediction was made): {len(gcat_empty)}\n")
                f.write("-" * 80 + "\n")

                gcat_empty_counts = gcat_empty.groupby(['Truth', 'Predicted']).size().reset_index(name='Count')
                gcat_empty_counts = gcat_empty_counts.sort_values('Count', ascending=False)

                f.write(f"{'Truth':<20} {'→':<3} {'Predicted':<20} {'Count':<10} {'%':<10}\n")
                f.write("-" * 80 + "\n")

                for _, row in gcat_empty_counts.iterrows():
                    percentage = (row['Count'] / len(gcat_empty)) * 100
                    f.write(f"{row['Truth']:<20} {'→':<3} {row['Predicted']:<20} {row['Count']:<10} {percentage:5.1f}%\n")

                f.write("\n")

        # SCat analysis
        if len(scat_mismatch_data) > 0:
            f.write("=" * 80 + "\n")
            f.write("SCAT MISMATCH ANALYSIS\n")
            f.write("=" * 80 + "\n\n")

            scat_df = pd.DataFrame(scat_mismatch_data)

            # Separate empty truth from regular mismatches
            scat_empty = scat_df[scat_df['Truth'] == '(empty)']
            scat_regular = scat_df[scat_df['Truth'] != '(empty)']

            # Regular mismatches
            if len(scat_regular) > 0:
                f.write(f"Regular Mismatches (both truth and prediction have values): {len(scat_regular)}\n")
                f.write("-" * 80 + "\n")

                scat_regular_counts = scat_regular.groupby(['Truth', 'Predicted']).size().reset_index(name='Count')
                scat_regular_counts = scat_regular_counts.sort_values('Count', ascending=False)

                f.write(f"{'Truth':<20} {'→':<3} {'Predicted':<20} {'Count':<10} {'%':<10}\n")
                f.write("-" * 80 + "\n")

                for _, row in scat_regular_counts.iterrows():
                    percentage = (row['Count'] / len(scat_regular)) * 100
                    f.write(f"{row['Truth']:<20} {'→':<3} {row['Predicted']:<20} {row['Count']:<10} {percentage:5.1f}%\n")

                f.write("\n")

            # Empty truth mismatches
            if len(scat_empty) > 0:
                f.write(f"Empty Truth Mismatches (truth is empty but prediction was made): {len(scat_empty)}\n")
                f.write("-" * 80 + "\n")

                scat_empty_counts = scat_empty.groupby(['Truth', 'Predicted']).size().reset_index(name='Count')
                scat_empty_counts = scat_empty_counts.sort_values('Count', ascending=False)

                f.write(f"{'Truth':<20} {'→':<3} {'Predicted':<20} {'Count':<10} {'%':<10}\n")
                f.write("-" * 80 + "\n")

                for _, row in scat_empty_counts.iterrows():
                    percentage = (row['Count'] / len(scat_empty)) * 100
                    f.write(f"{row['Truth']:<20} {'→':<3} {row['Predicted']:<20} {row['Count']:<10} {percentage:5.1f}%\n")

                f.write("\n")

        # Top 10 overall mismatches
        f.write("=" * 80 + "\n")
        f.write("TOP 10 MOST COMMON MISMATCHES (ALL CATEGORIES)\n")
        f.write("=" * 80 + "\n\n")

        if len(all_pairs) > 0:
            pairs_df_sorted = pairs_df.sort_values('Count', ascending=False).head(10)

            f.write(f"{'Rank':<6} {'Category':<10} {'Truth':<20} {'→':<3} {'Predicted':<20} {'Count':<10}\n")
            f.write("-" * 80 + "\n")

            for idx, (_, row) in enumerate(pairs_df_sorted.iterrows(), 1):
                f.write(f"{idx:<6} {row['Category']:<10} {row['Truth']:<20} {'→':<3} {row['Predicted']:<20} {row['Count']:<10}\n")

    print(f"[OK] Created mismatch text summary: {mismatch_text_report}")
else:
    print(f"\n[INFO] No mismatches found")

print("\n" + "=" * 80)
print(f"ALL REPORTS GENERATED SUCCESSFULLY!")
print(f"Check the '{output_dir}' folder for:")
print(f"  - Individual category reports (Category_XX_Full_Report.txt)")
print(f"  - Category-Suffix reports (Category_XX_Y_Report.txt)")
print(f"  - Overall suffix analysis")
print(f"  - Summary CSVs")
print(f"  - Mismatch_Summary.csv (detailed list of all mismatches)")
print(f"  - Mismatch_Counts_Summary.csv (counts of each mismatch pairing)")
print(f"  - Mismatch_Summary_Report.txt (text summary of all mismatches)")
print("=" * 80)
