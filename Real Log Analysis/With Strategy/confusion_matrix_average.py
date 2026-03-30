import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def normalize_gaming_value(value):
    """Normalize Gaming column values to Yes/No."""
    if pd.isna(value):
        return 'No'
    value = str(value).strip().lower()
    if value in ['yes', 'gaming', 'success']:
        return 'Yes'
    return 'No'

def create_confusion_matrix_for_run(truth_df, predictions_file, run_name):
    """Create a confusion matrix for a single run against ground truth."""

    # Handle CSV which may have extra trailing commas
    # Read only the first 5 columns we care about
    pred_df = pd.read_csv(predictions_file, usecols=[0, 1, 2, 3, 4],
                          names=['Filename', 'Gaming', 'Main Category', 'Subcategory', 'Success'],
                          skiprows=1)

    # Normalize column names
    pred_df.columns = pred_df.columns.str.strip()

    # Merge on Filename
    merged = pd.merge(truth_df, pred_df, on='Filename', suffixes=('_truth', '_pred'))

    # Normalize Gaming values
    merged['Truth'] = merged['Gaming_truth'].apply(normalize_gaming_value)
    merged['Predicted'] = merged['Gaming_pred'].apply(normalize_gaming_value)

    # Calculate confusion matrix components
    tp = len(merged[(merged['Truth'] == 'Yes') & (merged['Predicted'] == 'Yes')])  # True Positive
    tn = len(merged[(merged['Truth'] == 'No') & (merged['Predicted'] == 'No')])    # True Negative
    fp = len(merged[(merged['Truth'] == 'No') & (merged['Predicted'] == 'Yes')])   # False Positive
    fn = len(merged[(merged['Truth'] == 'Yes') & (merged['Predicted'] == 'No')])   # False Negative

    # Calculate metrics
    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0

    # Get misclassified files
    fp_files = merged[(merged['Truth'] == 'No') & (merged['Predicted'] == 'Yes')]['Filename'].tolist()
    fn_files = merged[(merged['Truth'] == 'Yes') & (merged['Predicted'] == 'No')]['Filename'].tolist()

    return {
        'run_name': run_name,
        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
        'total': total,
        'accuracy': accuracy, 'precision': precision,
        'recall': recall, 'f1': f1, 'specificity': specificity,
        'fp_files': fp_files, 'fn_files': fn_files
    }

def create_average_confusion_matrix(truth_file, run_files):
    """Create an average confusion matrix comparing multiple runs against ground truth."""

    # Load truth data once
    truth_df = pd.read_csv(truth_file)
    truth_df.columns = truth_df.columns.str.strip()

    # Collect results from each run
    results = []
    for run_file, run_name in run_files:
        if os.path.exists(run_file):
            result = create_confusion_matrix_for_run(truth_df, run_file, run_name)
            results.append(result)
            print(f"Processed {run_name}")
        else:
            print(f"Warning: {run_file} not found, skipping...")

    if not results:
        print("No valid run files found!")
        return

    # Print individual run results
    print()
    print("=" * 80)
    print("INDIVIDUAL RUN RESULTS")
    print("=" * 80)

    for r in results:
        print()
        print(f"--- {r['run_name']} ---")
        print(f"                     Predicted")
        print(f"                   Yes      No")
        print(f"              +---------+---------+")
        print(f"   Truth Yes  |   {r['tp']:3d}   |   {r['fn']:3d}   |")
        print(f"              +---------+---------+")
        print(f"   Truth No   |   {r['fp']:3d}   |   {r['tn']:3d}   |")
        print(f"              +---------+---------+")
        print(f"  Accuracy: {r['accuracy']:.4f}  Precision: {r['precision']:.4f}  Recall: {r['recall']:.4f}  F1: {r['f1']:.4f}")

    # Calculate averages
    n = len(results)
    avg_tp = sum(r['tp'] for r in results) / n
    avg_tn = sum(r['tn'] for r in results) / n
    avg_fp = sum(r['fp'] for r in results) / n
    avg_fn = sum(r['fn'] for r in results) / n
    avg_total = sum(r['total'] for r in results) / n

    avg_accuracy = sum(r['accuracy'] for r in results) / n
    avg_precision = sum(r['precision'] for r in results) / n
    avg_recall = sum(r['recall'] for r in results) / n
    avg_f1 = sum(r['f1'] for r in results) / n
    avg_specificity = sum(r['specificity'] for r in results) / n

    # Calculate standard deviations
    std_accuracy = np.std([r['accuracy'] for r in results])
    std_precision = np.std([r['precision'] for r in results])
    std_recall = np.std([r['recall'] for r in results])
    std_f1 = np.std([r['f1'] for r in results])
    std_specificity = np.std([r['specificity'] for r in results])

    # Print average confusion matrix
    print()
    print("=" * 80)
    print(f"AVERAGE CONFUSION MATRIX - Gaming Classification (n={n} runs)")
    print("=" * 80)
    print()
    print("                     Predicted")
    print("                   Yes      No")
    print("              +---------+---------+")
    print(f"   Truth Yes  |  {avg_tp:5.1f}  |  {avg_fn:5.1f}  |")
    print("              +---------+---------+")
    print(f"   Truth No   |  {avg_fp:5.1f}  |  {avg_tn:5.1f}  |")
    print("              +---------+---------+")
    print()
    print("-" * 80)
    print("AVERAGE METRICS (mean ± std)")
    print("-" * 80)
    print(f"  Avg Total Samples:     {avg_total:.1f}")
    print(f"  Avg True Positives:    {avg_tp:.1f}")
    print(f"  Avg True Negatives:    {avg_tn:.1f}")
    print(f"  Avg False Positives:   {avg_fp:.1f}")
    print(f"  Avg False Negatives:   {avg_fn:.1f}")
    print()
    print(f"  Accuracy:          {avg_accuracy:.4f} ± {std_accuracy:.4f} ({avg_accuracy*100:.2f}%)")
    print(f"  Precision:         {avg_precision:.4f} ± {std_precision:.4f} ({avg_precision*100:.2f}%)")
    print(f"  Recall:            {avg_recall:.4f} ± {std_recall:.4f} ({avg_recall*100:.2f}%)")
    print(f"  F1 Score:          {avg_f1:.4f} ± {std_f1:.4f}")
    print(f"  Specificity:       {avg_specificity:.4f} ± {std_specificity:.4f} ({avg_specificity*100:.2f}%)")
    print("=" * 80)

    # Aggregate misclassified files across runs
    print()
    print("MISCLASSIFICATION FREQUENCY ACROSS RUNS")
    print("-" * 80)

    # Count how often each file was a false positive
    fp_counts = {}
    for r in results:
        for f in r['fp_files']:
            fp_counts[f] = fp_counts.get(f, 0) + 1

    # Count how often each file was a false negative
    fn_counts = {}
    for r in results:
        for f in r['fn_files']:
            fn_counts[f] = fn_counts.get(f, 0) + 1

    if fp_counts:
        print("\nFalse Positives (Predicted Yes, Actually No):")
        for f, count in sorted(fp_counts.items(), key=lambda x: -x[1]):
            print(f"  - {f}: {count}/{n} runs")
    else:
        print("\nNo False Positives across any run")

    if fn_counts:
        print("\nFalse Negatives (Predicted No, Actually Yes):")
        for f, count in sorted(fn_counts.items(), key=lambda x: -x[1]):
            print(f"  - {f}: {count}/{n} runs")
    else:
        print("\nNo False Negatives across any run")

    # Write detailed misclassification report to file
    output_file = os.path.join(os.path.dirname(truth_file), "misclassifications_report.txt")
    with open(output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("MISCLASSIFICATIONS REPORT - All Runs\n")
        f.write("=" * 80 + "\n\n")

        for r in results:
            f.write(f"{'=' * 40}\n")
            f.write(f"{r['run_name']}\n")
            f.write(f"{'=' * 40}\n\n")

            f.write("FALSE POSITIVES (Predicted Yes, Actually No):\n")
            if r['fp_files']:
                for fp in sorted(r['fp_files']):
                    f.write(f"  - {fp}\n")
            else:
                f.write("  (none)\n")
            f.write("\n")

            f.write("FALSE NEGATIVES (Predicted No, Actually Yes):\n")
            if r['fn_files']:
                for fn in sorted(r['fn_files']):
                    f.write(f"  - {fn}\n")
            else:
                f.write("  (none)\n")
            f.write("\n\n")

        # Summary section
        f.write("=" * 80 + "\n")
        f.write("SUMMARY - Misclassification Frequency Across All Runs\n")
        f.write("=" * 80 + "\n\n")

        f.write("FALSE POSITIVES:\n")
        if fp_counts:
            for file, count in sorted(fp_counts.items(), key=lambda x: (-x[1], x[0])):
                f.write(f"  - {file}: {count}/{n} runs\n")
        else:
            f.write("  (none)\n")
        f.write("\n")

        f.write("FALSE NEGATIVES:\n")
        if fn_counts:
            for file, count in sorted(fn_counts.items(), key=lambda x: (-x[1], x[0])):
                f.write(f"  - {file}: {count}/{n} runs\n")
        else:
            f.write("  (none)\n")

    print(f"\nDetailed report saved to: {output_file}")

    # Write average confusion matrix report to file
    avg_output_file = os.path.join(os.path.dirname(truth_file), "average_confusion_matrix.txt")
    with open(avg_output_file, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write(f"AVERAGE CONFUSION MATRIX - Gaming Classification (n={n} runs)\n")
        f.write("=" * 80 + "\n\n")

        # Individual run results
        f.write("INDIVIDUAL RUN RESULTS\n")
        f.write("-" * 80 + "\n\n")

        for r in results:
            f.write(f"--- {r['run_name']} ---\n")
            f.write(f"                     Predicted\n")
            f.write(f"                   Yes      No\n")
            f.write(f"              +---------+---------+\n")
            f.write(f"   Truth Yes  |   {r['tp']:3d}   |   {r['fn']:3d}   |\n")
            f.write(f"              +---------+---------+\n")
            f.write(f"   Truth No   |   {r['fp']:3d}   |   {r['tn']:3d}   |\n")
            f.write(f"              +---------+---------+\n")
            f.write(f"  Accuracy: {r['accuracy']:.4f}  Precision: {r['precision']:.4f}  Recall: {r['recall']:.4f}  F1: {r['f1']:.4f}\n\n")

        # Average confusion matrix
        f.write("=" * 80 + "\n")
        f.write("AVERAGE CONFUSION MATRIX\n")
        f.write("=" * 80 + "\n\n")
        f.write("                     Predicted\n")
        f.write("                   Yes      No\n")
        f.write("              +---------+---------+\n")
        f.write(f"   Truth Yes  |  {avg_tp:5.1f}  |  {avg_fn:5.1f}  |\n")
        f.write("              +---------+---------+\n")
        f.write(f"   Truth No   |  {avg_fp:5.1f}  |  {avg_tn:5.1f}  |\n")
        f.write("              +---------+---------+\n\n")

        f.write("-" * 80 + "\n")
        f.write("AVERAGE METRICS (mean +/- std)\n")
        f.write("-" * 80 + "\n")
        f.write(f"  Avg Total Samples:     {avg_total:.1f}\n")
        f.write(f"  Avg True Positives:    {avg_tp:.1f}\n")
        f.write(f"  Avg True Negatives:    {avg_tn:.1f}\n")
        f.write(f"  Avg False Positives:   {avg_fp:.1f}\n")
        f.write(f"  Avg False Negatives:   {avg_fn:.1f}\n\n")
        f.write(f"  Accuracy:          {avg_accuracy:.4f} +/- {std_accuracy:.4f} ({avg_accuracy*100:.2f}%)\n")
        f.write(f"  Precision:         {avg_precision:.4f} +/- {std_precision:.4f} ({avg_precision*100:.2f}%)\n")
        f.write(f"  Recall:            {avg_recall:.4f} +/- {std_recall:.4f} ({avg_recall*100:.2f}%)\n")
        f.write(f"  F1 Score:          {avg_f1:.4f} +/- {std_f1:.4f}\n")
        f.write(f"  Specificity:       {avg_specificity:.4f} +/- {std_specificity:.4f} ({avg_specificity*100:.2f}%)\n")
        f.write("=" * 80 + "\n")

    print(f"Average confusion matrix saved to: {avg_output_file}")

    # Create boxplot for False Positives and False Negatives
    fp_values = [r['fp'] for r in results]
    fn_values = [r['fn'] for r in results]

    fig, ax = plt.subplots(figsize=(8, 6))
    bp = ax.boxplot([fp_values, fn_values], tick_labels=['False Positives', 'False Negatives'], patch_artist=True)

    # Color the boxes
    bp['boxes'][0].set_facecolor('lightcoral')
    bp['boxes'][1].set_facecolor('lightskyblue')

    ax.set_ylabel('Count')
    ax.set_title(f'Distribution of False Positives and False Negatives (n={n} runs)')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Add individual data points
    for i, (data, color) in enumerate([(fp_values, 'darkred'), (fn_values, 'darkblue')], 1):
        x = np.random.normal(i, 0.04, size=len(data))
        ax.scatter(x, data, alpha=0.6, color=color, s=30, zorder=3)

    plt.tight_layout()
    boxplot_file = os.path.join(os.path.dirname(truth_file), "fp_fn_boxplot.png")
    plt.savefig(boxplot_file, dpi=150)
    plt.show()
    print(f"Boxplot saved to: {boxplot_file}")

    # Write boxplot statistics to text file
    boxplot_stats_file = os.path.join(os.path.dirname(truth_file), "fp_fn_boxplot_stats.txt")
    with open(boxplot_stats_file, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write(f"BOXPLOT STATISTICS - FP and FN (n={n} runs)\n")
        f.write("=" * 60 + "\n\n")

        for name, values in [("False Positives", fp_values), ("False Negatives", fn_values)]:
            f.write(f"{name}:\n")
            f.write("-" * 40 + "\n")
            f.write(f"  Min:      {np.min(values)}\n")
            f.write(f"  Q1:       {np.percentile(values, 25):.2f}\n")
            f.write(f"  Median:   {np.median(values):.2f}\n")
            f.write(f"  Q3:       {np.percentile(values, 75):.2f}\n")
            f.write(f"  Max:      {np.max(values)}\n")
            f.write(f"  Mean:     {np.mean(values):.2f}\n")
            f.write(f"  Std Dev:  {np.std(values):.2f}\n")
            f.write("\n")

        f.write("=" * 60 + "\n")
        f.write("VALUES PER RUN\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Run':<10}{'False Positives':<20}{'False Negatives':<20}\n")
        f.write("-" * 50 + "\n")
        for r in results:
            f.write(f"{r['run_name']:<10}{r['fp']:<20}{r['fn']:<20}\n")

    print(f"Boxplot statistics saved to: {boxplot_stats_file}")

    return {
        'individual_results': results,
        'avg_tp': avg_tp, 'avg_tn': avg_tn, 'avg_fp': avg_fp, 'avg_fn': avg_fn,
        'avg_accuracy': avg_accuracy, 'avg_precision': avg_precision,
        'avg_recall': avg_recall, 'avg_f1': avg_f1, 'avg_specificity': avg_specificity,
        'std_accuracy': std_accuracy, 'std_precision': std_precision,
        'std_recall': std_recall, 'std_f1': std_f1, 'std_specificity': std_specificity
    }

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    truth_file = os.path.join(script_dir, "Truth.csv")

    # Define the run files
    run_files = [
        (os.path.join(script_dir, "Run1.csv"), "Run 1"),
        (os.path.join(script_dir, "Run2.csv"), "Run 2"),
        (os.path.join(script_dir, "Run3.csv"), "Run 3"),
        (os.path.join(script_dir, "Run4.csv"), "Run 4"),
        (os.path.join(script_dir, "Run5.csv"), "Run 5"),
        (os.path.join(script_dir, "Run6.csv"), "Run 6"),
        (os.path.join(script_dir, "Run7.csv"), "Run 7"),
        (os.path.join(script_dir, "Run8.csv"), "Run 8"),
        (os.path.join(script_dir, "Run9.csv"), "Run 9"),
        (os.path.join(script_dir, "Run10.csv"), "Run 10"),
    ]

    create_average_confusion_matrix(truth_file, run_files)
