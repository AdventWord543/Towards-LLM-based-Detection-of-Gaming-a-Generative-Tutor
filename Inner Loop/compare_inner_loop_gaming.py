import pandas as pd
import numpy as np
import os

# Read the CSV files
truth_df = pd.read_csv('Inner Loop Truth.csv')
predicted_df = pd.read_csv('filename_gaming.csv')

# Normalize the ID column in predicted_df (remove .txt extension)
predicted_df['ID'] = predicted_df['Filename'].str.replace('.txt', '', regex=False)

# Reorder columns: ID first, then Gaming1-10
gaming_cols = [f'Gaming{i}' for i in range(1, 11)]
predicted_df = predicted_df[['ID'] + gaming_cols]

# Rename columns for easier comparison
truth_cols = ['ID'] + [f'Truth_{i}' for i in range(1, 11)]
pred_cols = ['ID'] + [f'Pred_{i}' for i in range(1, 11)]

truth_df.columns = truth_cols
predicted_df.columns = pred_cols

# Convert predicted values: Gaming -> Yes, Genuine -> No
for col in pred_cols[1:]:
    predicted_df[col] = predicted_df[col].replace({'Gaming': 'Yes', 'Genuine': 'No'})

# Merge the dataframes on ID
merged_df = pd.merge(truth_df, predicted_df, on='ID', how='outer', indicator=True)

# Report merge results
both = merged_df[merged_df['_merge'] == 'both']
left_only = merged_df[merged_df['_merge'] == 'left_only']
right_only = merged_df[merged_df['_merge'] == 'right_only']

print(f"IDs in both files: {len(both)}")
print(f"IDs only in Truth: {len(left_only)}")
print(f"IDs only in Predicted: {len(right_only)}")

# Keep only matched IDs for comparison
merged_df = both.drop(columns=['_merge'])

# Function to calculate gaming accuracy across all rounds
def calculate_gaming_accuracy(df):
    """Calculate accuracy across all rounds for gaming predictions"""
    total_matches = 0
    total_valid = 0

    for i in range(1, 11):
        truth_col = f'Truth_{i}'
        pred_col = f'Pred_{i}'

        # Valid comparisons: both have values (not NaN and not empty string)
        valid_mask = (df[truth_col].notna() & (df[truth_col] != '')) & \
                     (df[pred_col].notna() & (df[pred_col] != ''))

        matches = (df.loc[valid_mask, truth_col] == df.loc[valid_mask, pred_col]).sum()
        total_matches += matches
        total_valid += valid_mask.sum()

    if total_valid == 0:
        return 0.0, 0, 0

    accuracy = (total_matches / total_valid) * 100
    return accuracy, total_matches, total_valid

# Function to calculate accuracy for a specific round
def calculate_round_accuracy(df, round_num):
    """Calculate accuracy for a specific round"""
    truth_col = f'Truth_{round_num}'
    pred_col = f'Pred_{round_num}'

    valid_mask = (df[truth_col].notna() & (df[truth_col] != '')) & \
                 (df[pred_col].notna() & (df[pred_col] != ''))

    if valid_mask.sum() == 0:
        return 0.0, 0, 0

    matches = (df.loc[valid_mask, truth_col] == df.loc[valid_mask, pred_col]).sum()
    total = valid_mask.sum()
    accuracy = (matches / total) * 100

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
output_dir = 'Inner_Loop_Gaming_Reports'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("\n" + "=" * 80)
print("GENERATING INNER LOOP GAMING ACCURACY REPORTS")
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
    f.write("OVERALL GAMING ACCURACY ANALYSIS BY SUFFIX (_A, _B, _C)\n")
    f.write("=" * 80 + "\n\n")

    for suffix in suffixes:
        suffix_df = merged_df[merged_df['Suffix'] == suffix]

        if len(suffix_df) > 0:
            gaming_acc, gaming_match, gaming_total = calculate_gaming_accuracy(suffix_df)

            f.write(f"SUFFIX {suffix}:\n")
            f.write("-" * 80 + "\n")
            f.write(f"Gaming:        {gaming_acc:6.2f}% ({gaming_match}/{gaming_total} correct)\n")
            f.write(f"Total IDs:     {len(suffix_df)}\n\n")

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
                gaming_acc, gaming_match, gaming_total = calculate_gaming_accuracy(pattern_suffix_df)
                f.write(f"  Pattern {pattern}: Gaming {gaming_acc:6.2f}% ({gaming_match}/{gaming_total})\n")
        f.write("\n")

    # Breakdown by round
    f.write("=" * 80 + "\n")
    f.write("ACCURACY BY ROUND (OVERALL)\n")
    f.write("=" * 80 + "\n\n")

    for i in range(1, 11):
        round_acc, round_match, round_total = calculate_round_accuracy(merged_df, i)
        if round_total > 0:
            f.write(f"Round {i:2d}: {round_acc:6.2f}% ({round_match}/{round_total})\n")

    # Detailed breakdown for each round
    f.write("\n" + "=" * 80 + "\n")
    f.write("DETAILED BREAKDOWN BY ROUND\n")
    f.write("=" * 80 + "\n")

    for i in range(1, 11):
        round_acc, round_match, round_total = calculate_round_accuracy(merged_df, i)
        if round_total > 0:
            f.write(f"\n{'='*80}\n")
            f.write(f"ROUND {i}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Overall: {round_acc:6.2f}% ({round_match}/{round_total})\n\n")

            # Accuracy by category for this round
            f.write("  By Category:\n")
            f.write("  " + "-" * 40 + "\n")
            for num in sorted(merged_df['Number'].unique()):
                num_df = merged_df[merged_df['Number'] == num]
                cat_acc, cat_match, cat_total = calculate_round_accuracy(num_df, i)
                if cat_total > 0:
                    f.write(f"    Category {num}: {cat_acc:6.2f}% ({cat_match}/{cat_total})\n")

            # Accuracy by suffix for this round
            f.write("\n  By Suffix (_A, _B, _C):\n")
            f.write("  " + "-" * 40 + "\n")
            for suffix in suffixes:
                suffix_df = merged_df[merged_df['Suffix'] == suffix]
                suff_acc, suff_match, suff_total = calculate_round_accuracy(suffix_df, i)
                if suff_total > 0:
                    f.write(f"    {suffix}: {suff_acc:6.2f}% ({suff_match}/{suff_total})\n")

            # Accuracy by strategy/pattern for this round
            f.write("\n  By Strategy (.1., .2., .3., .4.):\n")
            f.write("  " + "-" * 40 + "\n")
            patterns = ['.1.', '.2.', '.3.', '.4.']
            for pattern in patterns:
                pattern_df = merged_df[merged_df['Pattern'] == pattern]
                pat_acc, pat_match, pat_total = calculate_round_accuracy(pattern_df, i)
                if pat_total > 0:
                    f.write(f"    {pattern}: {pat_acc:6.2f}% ({pat_match}/{pat_total})\n")

print(f"[OK] Created overall suffix analysis: {overall_suffix_report}")

# Generate individual reports for each number
for num in numbers:
    num_df = merged_df[merged_df['Number'] == num]

    # Create report filename
    report_filename = os.path.join(output_dir, f'Category_{num}_Gaming_Report.txt')

    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"GAMING ACCURACY REPORT FOR CATEGORY {num}\n")
        f.write("=" * 80 + "\n\n")

        # Overall accuracy for this category
        gaming_acc, gaming_match, gaming_total = calculate_gaming_accuracy(num_df)

        f.write("OVERALL GAMING ACCURACY FOR CATEGORY " + num + ":\n")
        f.write("-" * 80 + "\n")
        f.write(f"Gaming:        {gaming_acc:6.2f}% ({gaming_match}/{gaming_total} correct)\n\n")

        # Store for summary
        summary_report.append({
            'Category': num,
            'Gaming_Acc': gaming_acc,
            'Gaming_Match': f"{gaming_match}/{gaming_total}"
        })

        # Breakdown by suffix
        f.write("BREAKDOWN BY SUFFIX (_A, _B, _C):\n")
        f.write("=" * 80 + "\n")

        for suffix in suffixes:
            suffix_df = num_df[num_df['Suffix'] == suffix]

            if len(suffix_df) > 0:
                s_gaming_acc, s_gaming_match, s_gaming_total = calculate_gaming_accuracy(suffix_df)

                f.write(f"\nSuffix {suffix}:\n")
                f.write(f"  Gaming:        {s_gaming_acc:6.2f}% ({s_gaming_match}/{s_gaming_total})\n")

                # Store suffix summary
                suffix_summary_report.append({
                    'Category': num,
                    'Suffix': suffix,
                    'Gaming_Acc': s_gaming_acc,
                    'Gaming_Match': f"{s_gaming_match}/{s_gaming_total}"
                })

        f.write("\n")

        # Breakdown by pattern
        f.write("BREAKDOWN BY PATTERN:\n")
        f.write("-" * 80 + "\n")
        patterns = ['.1.', '.2.', '.3.', '.4.']

        for pattern in patterns:
            pattern_df = num_df[num_df['Pattern'] == pattern]

            if len(pattern_df) > 0:
                p_gaming_acc, p_gaming_match, p_gaming_total = calculate_gaming_accuracy(pattern_df)
                f.write(f"\nPattern {pattern}:\n")
                f.write(f"  Gaming:        {p_gaming_acc:6.2f}% ({p_gaming_match}/{p_gaming_total})\n")

        f.write("\n")

        # Breakdown by pattern and suffix combined
        f.write("BREAKDOWN BY PATTERN AND SUFFIX COMBINED:\n")
        f.write("=" * 80 + "\n")

        for pattern in patterns:
            f.write(f"\nPattern {pattern}:\n")
            f.write("-" * 40 + "\n")

            for suffix in suffixes:
                ps_df = num_df[(num_df['Pattern'] == pattern) & (num_df['Suffix'] == suffix)]

                if len(ps_df) > 0:
                    ps_gaming_acc, ps_gaming_match, ps_gaming_total = calculate_gaming_accuracy(ps_df)
                    f.write(f"  {suffix}: Gaming {ps_gaming_acc:6.2f}% ({ps_gaming_match}/{ps_gaming_total})\n")

        f.write("\n")

        # Round-by-round accuracy for this category
        f.write("ACCURACY BY ROUND:\n")
        f.write("-" * 80 + "\n")

        for i in range(1, 11):
            round_acc, round_match, round_total = calculate_round_accuracy(num_df, i)
            if round_total > 0:
                f.write(f"Round {i:2d}: {round_acc:6.2f}% ({round_match}/{round_total})\n")

        f.write("\n")

        # Detailed comparison table (grouped by suffix)
        f.write("DETAILED ITEM-BY-ITEM COMPARISON (GROUPED BY SUFFIX):\n")
        f.write("=" * 80 + "\n")

        for suffix in suffixes:
            suffix_df = num_df[num_df['Suffix'] == suffix]

            if len(suffix_df) > 0:
                f.write(f"\nSUFFIX {suffix}:\n")
                header = f"{'ID':<15} "
                for i in range(1, 11):
                    header += f"R{i:<3} "
                header += "Status\n"
                f.write(header)
                f.write("-" * 80 + "\n")

                for _, row in suffix_df.iterrows():
                    f.write(f"{row['ID']:<15} ")

                    all_match = True
                    has_data = False

                    for i in range(1, 11):
                        truth_val = row[f'Truth_{i}']
                        pred_val = row[f'Pred_{i}']

                        # Check if both have values
                        truth_valid = pd.notna(truth_val) and truth_val != ''
                        pred_valid = pd.notna(pred_val) and pred_val != ''

                        if truth_valid and pred_valid:
                            has_data = True
                            if truth_val == pred_val:
                                f.write("Y   ")
                            else:
                                f.write("N   ")
                                all_match = False
                        else:
                            f.write("-   ")

                    if has_data:
                        status = "PERFECT" if all_match else "MISMATCH"
                    else:
                        status = "EMPTY"
                    f.write(f"{status}\n")

        f.write("\n")

        # Mismatch summary
        mismatch_count = 0
        mismatch_details = []

        for _, row in num_df.iterrows():
            for i in range(1, 11):
                truth_val = row[f'Truth_{i}']
                pred_val = row[f'Pred_{i}']

                truth_valid = pd.notna(truth_val) and truth_val != ''
                pred_valid = pd.notna(pred_val) and pred_val != ''

                if truth_valid and pred_valid and truth_val != pred_val:
                    mismatch_count += 1
                    mismatch_details.append({
                        'ID': row['ID'],
                        'Round': i,
                        'Truth': truth_val,
                        'Predicted': pred_val
                    })

        f.write("MISMATCH SUMMARY:\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total gaming mismatches: {mismatch_count}\n\n")

        if mismatch_count > 0:
            f.write("MISMATCH DETAILS:\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'ID':<15} {'Round':<8} {'Truth':<10} {'Predicted':<10}\n")
            f.write("-" * 80 + "\n")

            for m in mismatch_details:
                f.write(f"{m['ID']:<15} {m['Round']:<8} {m['Truth']:<10} {m['Predicted']:<10}\n")

        f.write("\n")

    print(f"[OK] Created report for Category {num}: {report_filename}")

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
    f.write("MASTER SUMMARY REPORT - INNER LOOP GAMING ACCURACY\n")
    f.write("=" * 80 + "\n\n")

    f.write(f"{'Category':<10} {'Gaming Acc':<20}\n")
    f.write("-" * 80 + "\n")

    for item in summary_report:
        f.write(f"{item['Category']:<10} ")
        f.write(f"{item['Gaming_Acc']:6.2f}% ({item['Gaming_Match']:<10})\n")

    f.write("\n" + "=" * 80 + "\n")
    f.write("BREAKDOWN BY SUFFIX\n")
    f.write("=" * 80 + "\n\n")

    for suffix in suffixes:
        suffix_df = merged_df[merged_df['Suffix'] == suffix]

        if len(suffix_df) > 0:
            gaming_acc, gaming_match, gaming_total = calculate_gaming_accuracy(suffix_df)

            f.write(f"ALL {suffix} files:\n")
            f.write(f"  Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n\n")

    f.write("=" * 80 + "\n")
    f.write("OVERALL STATISTICS\n")
    f.write("=" * 80 + "\n\n")

    gaming_acc, gaming_match, gaming_total = calculate_gaming_accuracy(merged_df)
    f.write(f"Overall Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n\n")

    f.write("Range 01-14:\n")
    range_01_14 = merged_df[merged_df['Number'].isin([f'{i:02d}' for i in range(1, 15)])]
    gaming_acc, gaming_match, gaming_total = calculate_gaming_accuracy(range_01_14)
    f.write(f"  Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n\n")

    f.write("Range 16-19:\n")
    range_16_19 = merged_df[merged_df['Number'].isin([f'{i:02d}' for i in range(16, 20)])]
    gaming_acc, gaming_match, gaming_total = calculate_gaming_accuracy(range_16_19)
    f.write(f"  Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n\n")

    f.write("By Pattern:\n")
    patterns = ['.1.', '.2.', '.3.', '.4.']
    for pattern in patterns:
        pattern_df = merged_df[merged_df['Pattern'] == pattern]
        if len(pattern_df) > 0:
            gaming_acc, gaming_match, gaming_total = calculate_gaming_accuracy(pattern_df)
            f.write(f"  Pattern {pattern}:\n")
            f.write(f"    Gaming:        {gaming_acc:.2f}% ({gaming_match}/{gaming_total})\n")

    f.write("\n")
    f.write("By Round:\n")
    for i in range(1, 11):
        round_acc, round_match, round_total = calculate_round_accuracy(merged_df, i)
        if round_total > 0:
            f.write(f"  Round {i:2d}: {round_acc:.2f}% ({round_match}/{round_total})\n")

    # Detailed breakdown for each round
    f.write("\n" + "=" * 80 + "\n")
    f.write("DETAILED BREAKDOWN BY ROUND\n")
    f.write("=" * 80 + "\n")

    for i in range(1, 11):
        round_acc, round_match, round_total = calculate_round_accuracy(merged_df, i)
        if round_total > 0:
            f.write(f"\n{'='*80}\n")
            f.write(f"ROUND {i}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Overall: {round_acc:.2f}% ({round_match}/{round_total})\n\n")

            # Accuracy by category for this round
            f.write("  By Category:\n")
            f.write("  " + "-" * 40 + "\n")
            for num in sorted(merged_df['Number'].unique()):
                num_df = merged_df[merged_df['Number'] == num]
                cat_acc, cat_match, cat_total = calculate_round_accuracy(num_df, i)
                if cat_total > 0:
                    f.write(f"    Category {num}: {cat_acc:6.2f}% ({cat_match}/{cat_total})\n")

            # Accuracy by suffix for this round
            f.write("\n  By Suffix (_A, _B, _C):\n")
            f.write("  " + "-" * 40 + "\n")
            suffixes_list = ['_A', '_B', '_C']
            for suffix in suffixes_list:
                suffix_df = merged_df[merged_df['Suffix'] == suffix]
                suff_acc, suff_match, suff_total = calculate_round_accuracy(suffix_df, i)
                if suff_total > 0:
                    f.write(f"    {suffix}: {suff_acc:6.2f}% ({suff_match}/{suff_total})\n")

            # Accuracy by strategy/pattern for this round
            f.write("\n  By Strategy (.1., .2., .3., .4.):\n")
            f.write("  " + "-" * 40 + "\n")
            patterns_list = ['.1.', '.2.', '.3.', '.4.']
            for pattern in patterns_list:
                pattern_df = merged_df[merged_df['Pattern'] == pattern]
                pat_acc, pat_match, pat_total = calculate_round_accuracy(pattern_df, i)
                if pat_total > 0:
                    f.write(f"    {pattern}: {pat_acc:6.2f}% ({pat_match}/{pat_total})\n")

print(f"[OK] Created master summary: {master_report}")

# ===== CREATE ROUND-BY-ROUND BREAKDOWN CSV =====
round_breakdown_data = []

for i in range(1, 11):
    # Overall for this round
    round_acc, round_match, round_total = calculate_round_accuracy(merged_df, i)
    if round_total > 0:
        round_breakdown_data.append({
            'Round': i,
            'Group_Type': 'Overall',
            'Group_Value': 'All',
            'Accuracy': round_acc,
            'Correct': round_match,
            'Total': round_total
        })

        # By category
        for num in sorted(merged_df['Number'].unique()):
            num_df = merged_df[merged_df['Number'] == num]
            cat_acc, cat_match, cat_total = calculate_round_accuracy(num_df, i)
            if cat_total > 0:
                round_breakdown_data.append({
                    'Round': i,
                    'Group_Type': 'Category',
                    'Group_Value': num,
                    'Accuracy': cat_acc,
                    'Correct': cat_match,
                    'Total': cat_total
                })

        # By suffix (_A, _B, _C)
        for suffix in suffixes:
            suffix_df = merged_df[merged_df['Suffix'] == suffix]
            suff_acc, suff_match, suff_total = calculate_round_accuracy(suffix_df, i)
            if suff_total > 0:
                round_breakdown_data.append({
                    'Round': i,
                    'Group_Type': 'Suffix',
                    'Group_Value': suffix,
                    'Accuracy': suff_acc,
                    'Correct': suff_match,
                    'Total': suff_total
                })

        # By strategy/pattern (.1., .2., .3., .4.)
        patterns = ['.1.', '.2.', '.3.', '.4.']
        for pattern in patterns:
            pattern_df = merged_df[merged_df['Pattern'] == pattern]
            pat_acc, pat_match, pat_total = calculate_round_accuracy(pattern_df, i)
            if pat_total > 0:
                round_breakdown_data.append({
                    'Round': i,
                    'Group_Type': 'Strategy',
                    'Group_Value': pattern,
                    'Accuracy': pat_acc,
                    'Correct': pat_match,
                    'Total': pat_total
                })

if len(round_breakdown_data) > 0:
    round_breakdown_df = pd.DataFrame(round_breakdown_data)
    round_breakdown_csv = os.path.join(output_dir, 'Round_By_Round_Breakdown.csv')
    round_breakdown_df.to_csv(round_breakdown_csv, index=False)
    print(f"[OK] Created round-by-round breakdown CSV: {round_breakdown_csv}")

# ===== CREATE ROUND-BY-ROUND BREAKDOWN TEXT REPORT =====
round_breakdown_report = os.path.join(output_dir, 'Round_By_Round_Breakdown.txt')
with open(round_breakdown_report, 'w', encoding='utf-8') as f:
    f.write("=" * 80 + "\n")
    f.write("ROUND-BY-ROUND ACCURACY BREAKDOWN\n")
    f.write("Accuracy by Category and Strategy for Each Round\n")
    f.write("=" * 80 + "\n\n")

    for i in range(1, 11):
        round_acc, round_match, round_total = calculate_round_accuracy(merged_df, i)
        if round_total > 0:
            f.write("=" * 80 + "\n")
            f.write(f"ROUND {i}\n")
            f.write("=" * 80 + "\n")
            f.write(f"Overall Accuracy: {round_acc:.2f}% ({round_match}/{round_total})\n\n")

            # Accuracy by category
            f.write("ACCURACY BY CATEGORY:\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Category':<12} {'Accuracy':<12} {'Correct/Total':<15}\n")
            f.write("-" * 60 + "\n")

            for num in sorted(merged_df['Number'].unique()):
                num_df = merged_df[merged_df['Number'] == num]
                cat_acc, cat_match, cat_total = calculate_round_accuracy(num_df, i)
                if cat_total > 0:
                    f.write(f"{num:<12} {cat_acc:6.2f}%      {cat_match}/{cat_total}\n")

            f.write("\n")

            # Accuracy by suffix
            f.write("ACCURACY BY SUFFIX (_A, _B, _C):\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Suffix':<12} {'Accuracy':<12} {'Correct/Total':<15}\n")
            f.write("-" * 60 + "\n")

            for suffix in suffixes:
                suffix_df = merged_df[merged_df['Suffix'] == suffix]
                suff_acc, suff_match, suff_total = calculate_round_accuracy(suffix_df, i)
                if suff_total > 0:
                    f.write(f"{suffix:<12} {suff_acc:6.2f}%      {suff_match}/{suff_total}\n")

            f.write("\n")

            # Accuracy by strategy/pattern
            f.write("ACCURACY BY STRATEGY (.1., .2., .3., .4.):\n")
            f.write("-" * 60 + "\n")
            f.write(f"{'Strategy':<12} {'Accuracy':<12} {'Correct/Total':<15}\n")
            f.write("-" * 60 + "\n")

            patterns = ['.1.', '.2.', '.3.', '.4.']
            for pattern in patterns:
                pattern_df = merged_df[merged_df['Pattern'] == pattern]
                pat_acc, pat_match, pat_total = calculate_round_accuracy(pattern_df, i)
                if pat_total > 0:
                    f.write(f"{pattern:<12} {pat_acc:6.2f}%      {pat_match}/{pat_total}\n")

            f.write("\n\n")

print(f"[OK] Created round-by-round breakdown report: {round_breakdown_report}")

# ===== CREATE MISMATCH SUMMARY CSV =====
mismatch_data = []

for _, row in merged_df.iterrows():
    for i in range(1, 11):
        truth_val = row[f'Truth_{i}']
        pred_val = row[f'Pred_{i}']

        truth_valid = pd.notna(truth_val) and truth_val != ''
        pred_valid = pd.notna(pred_val) and pred_val != ''

        if truth_valid and pred_valid and truth_val != pred_val:
            mismatch_data.append({
                'ID': row['ID'],
                'Round': i,
                'Truth': truth_val,
                'Predicted': pred_val,
                'Category': row['Number'],
                'Pattern': row['Pattern'],
                'Suffix': row['Suffix']
            })

if len(mismatch_data) > 0:
    mismatch_df = pd.DataFrame(mismatch_data)
    mismatch_csv = os.path.join(output_dir, 'Gaming_Mismatches.csv')
    mismatch_df.to_csv(mismatch_csv, index=False)
    print(f"\n[OK] Created mismatch CSV: {mismatch_csv}")
    print(f"     Total gaming mismatches: {len(mismatch_data)}")

    # Mismatch counts by type
    mismatch_counts = mismatch_df.groupby(['Truth', 'Predicted']).size().reset_index(name='Count')
    mismatch_counts = mismatch_counts.sort_values('Count', ascending=False)
    mismatch_counts_csv = os.path.join(output_dir, 'Gaming_Mismatch_Counts.csv')
    mismatch_counts.to_csv(mismatch_counts_csv, index=False)
    print(f"[OK] Created mismatch counts CSV: {mismatch_counts_csv}")

    # Mismatch text report
    mismatch_report = os.path.join(output_dir, 'Gaming_Mismatch_Report.txt')
    with open(mismatch_report, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("GAMING MISMATCH REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Total mismatches: {len(mismatch_data)}\n\n")

        f.write("MISMATCH TYPES:\n")
        f.write("-" * 80 + "\n")
        for _, row in mismatch_counts.iterrows():
            percentage = (row['Count'] / len(mismatch_data)) * 100
            f.write(f"Truth: {row['Truth']:<10} -> Predicted: {row['Predicted']:<10} Count: {row['Count']:4d} ({percentage:5.1f}%)\n")

        f.write("\n")
        f.write("MISMATCHES BY SUFFIX:\n")
        f.write("-" * 80 + "\n")
        for suffix in suffixes:
            suffix_mismatches = mismatch_df[mismatch_df['Suffix'] == suffix]
            f.write(f"{suffix}: {len(suffix_mismatches)} mismatches\n")

        f.write("\n")
        f.write("MISMATCHES BY ROUND:\n")
        f.write("-" * 80 + "\n")
        for i in range(1, 11):
            round_mismatches = mismatch_df[mismatch_df['Round'] == i]
            if len(round_mismatches) > 0:
                f.write(f"Round {i:2d}: {len(round_mismatches)} mismatches\n")

    print(f"[OK] Created mismatch report: {mismatch_report}")
else:
    print(f"\n[INFO] No mismatches found - perfect accuracy!")

print("\n" + "=" * 80)
print("ALL REPORTS GENERATED SUCCESSFULLY!")
print(f"Check the '{output_dir}' folder for:")
print("  - Individual category reports (Category_XX_Gaming_Report.txt)")
print("  - Overall suffix analysis")
print("  - Round-by-round breakdown (Round_By_Round_Breakdown.txt/.csv)")
print("  - Summary CSVs")
print("  - Gaming mismatch reports")
print("=" * 80)
