import pandas as pd
import numpy as np

def normalize_gaming_value(value):
    """Normalize Gaming column values to Yes/No."""
    if pd.isna(value):
        return 'No'
    value = str(value).strip().lower()
    if value in ['yes', 'gaming', 'success']:
        return 'Yes'
    return 'No'

def create_confusion_matrix(truth_file, predictions_file):
    """Create a confusion matrix comparing predictions against ground truth."""

    # Load the data
    truth_df = pd.read_csv(truth_file)

    # Handle classifications.csv which may have extra trailing commas
    # Read only the first 5 columns we care about
    pred_df = pd.read_csv(predictions_file, usecols=[0, 1, 2, 3, 4],
                          names=['Filename', 'Gaming', 'Main Category', 'Subcategory', 'Success'],
                          skiprows=1)

    # Normalize column names
    truth_df.columns = truth_df.columns.str.strip()
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

    # Print results
    print("=" * 60)
    print("CONFUSION MATRIX - Gaming Classification")
    print("=" * 60)
    print()
    print("                     Predicted")
    print("                   Yes      No")
    print("              +---------+---------+")
    print(f"   Truth Yes  |   {tp:3d}   |   {fn:3d}   |")
    print("              +---------+---------+")
    print(f"   Truth No   |   {fp:3d}   |   {tn:3d}   |")
    print("              +---------+---------+")
    print()
    print("-" * 60)
    print("METRICS")
    print("-" * 60)
    print(f"  Total Samples:     {total}")
    print(f"  True Positives:    {tp}")
    print(f"  True Negatives:    {tn}")
    print(f"  False Positives:   {fp}")
    print(f"  False Negatives:   {fn}")
    print()
    print(f"  Accuracy:          {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision:         {precision:.4f} ({precision*100:.2f}%)")
    print(f"  Recall:            {recall:.4f} ({recall*100:.2f}%)")
    print(f"  F1 Score:          {f1:.4f}")
    print(f"  Specificity:       {specificity:.4f} ({specificity*100:.2f}%)")
    print("=" * 60)

    # Show misclassified files
    print()
    print("MISCLASSIFIED FILES")
    print("-" * 60)

    fp_files = merged[(merged['Truth'] == 'No') & (merged['Predicted'] == 'Yes')]['Filename'].tolist()
    fn_files = merged[(merged['Truth'] == 'Yes') & (merged['Predicted'] == 'No')]['Filename'].tolist()

    if fp_files:
        print("\nFalse Positives (Predicted Yes, Actually No):")
        for f in fp_files:
            print(f"  - {f}")
    else:
        print("\nNo False Positives")

    if fn_files:
        print("\nFalse Negatives (Predicted No, Actually Yes):")
        for f in fn_files:
            print(f"  - {f}")
    else:
        print("\nNo False Negatives")

    # Check for files only in one dataset
    truth_files = set(truth_df['Filename'])
    pred_files = set(pred_df['Filename'])

    only_in_truth = truth_files - pred_files
    only_in_pred = pred_files - truth_files

    if only_in_truth or only_in_pred:
        print()
        print("-" * 60)
        print("FILE MISMATCHES")
        print("-" * 60)
        if only_in_truth:
            print(f"\nFiles only in Truth.csv ({len(only_in_truth)}):")
            for f in sorted(only_in_truth):
                print(f"  - {f}")
        if only_in_pred:
            print(f"\nFiles only in classifications.csv ({len(only_in_pred)}):")
            for f in sorted(only_in_pred):
                print(f"  - {f}")

    return {
        'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn,
        'accuracy': accuracy, 'precision': precision,
        'recall': recall, 'f1': f1, 'specificity': specificity
    }

if __name__ == "__main__":
    import os

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    truth_file = os.path.join(script_dir, "Truth.csv")
    predictions_file = os.path.join(script_dir, "classifications.csv")

    create_confusion_matrix(truth_file, predictions_file)
