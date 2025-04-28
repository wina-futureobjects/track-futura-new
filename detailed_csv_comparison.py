import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

def detailed_csv_comparison(file1, file2, output_file=None):
    """
    Compare two CSV files row by row and create a detailed comparison
    showing differences between matching records.
    
    Args:
        file1: Path to first CSV file
        file2: Path to second CSV file
        output_file: Optional path for output file, if None generates a timestamped filename
    
    Returns:
        Path to the generated comparison file
    """
    print(f"Comparing {file1} and {file2}...")
    
    # Load files with pandas, try different encodings if needed
    try:
        df1 = pd.read_csv(file1, encoding='utf-8')
        df2 = pd.read_csv(file2, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df1 = pd.read_csv(file1, encoding='latin1')
            df2 = pd.read_csv(file2, encoding='latin1')
        except Exception as e:
            print(f"Error reading files: {e}")
            return None
    
    # Print basic file statistics
    print(f"File 1 ({file1}) - Rows: {len(df1)}, Columns: {len(df1.columns)}")
    print(f"File 2 ({file2}) - Rows: {len(df2)}, Columns: {len(df2.columns)}")
    
    # Determine common columns and create a key for matching records
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    common_cols = list(cols1.intersection(cols2))
    
    # For matching rows, use a key column if specified or try some common identifiers
    # Typically 'Post URL' is a good key for social media data
    potential_keys = ['Post URL', 'url', 'post_id', 'id', 'ID']
    key_col = None
    
    for key in potential_keys:
        if key in common_cols:
            key_col = key
            break
    
    if not key_col:
        print("No suitable key column found to match records. Available columns:")
        print(f"File 1: {sorted(list(cols1))}")
        print(f"File 2: {sorted(list(cols2))}")
        return None
    
    print(f"Using '{key_col}' as the key for matching records")
    
    # Rename columns to indicate source
    df1_renamed = df1.copy()
    df2_renamed = df2.copy()
    
    # Keep original key column name the same for merging
    for col in df1.columns:
        if col != key_col:
            df1_renamed = df1_renamed.rename(columns={col: f"{col}_file1"})
    
    for col in df2.columns:
        if col != key_col:
            df2_renamed = df2_renamed.rename(columns={col: f"{col}_file2"})
    
    # Merge dataframes on the key column
    merged_df = pd.merge(df1_renamed, df2_renamed, on=key_col, how='outer', indicator=True)
    
    # Add indicator for which file the row is from
    merged_df['Source'] = merged_df['_merge'].map({
        'left_only': f'Only in {os.path.basename(file1)}',
        'right_only': f'Only in {os.path.basename(file2)}',
        'both': 'In both files'
    })
    
    # Remove the pandas-generated _merge column 
    merged_df = merged_df.drop(columns=['_merge'])
    
    # Create difference indicators
    for col in common_cols:
        if col != key_col:
            col1 = f"{col}_file1"
            col2 = f"{col}_file2"
            
            # Only include difference columns that exist in both files
            if col1 in merged_df.columns and col2 in merged_df.columns:
                # Create a new column to indicate differences
                diff_col = f"{col}_diff"
                
                # Compare values with handling for NaN
                merged_df[diff_col] = ''
                
                # We need to handle different types of comparisons
                mask = merged_df['Source'] == 'In both files'
                
                # Convert columns to string for comparison if they have different types
                col1_values = merged_df.loc[mask, col1].astype(str)
                col2_values = merged_df.loc[mask, col2].astype(str)
                
                # Mark different values
                merged_df.loc[mask & (col1_values != col2_values), diff_col] = 'DIFFERENT'
                
                # Handle NaN specially
                merged_df.loc[mask & (merged_df[col1].isna() & ~merged_df[col2].isna()), diff_col] = 'DIFFERENT (null vs value)'
                merged_df.loc[mask & (~merged_df[col1].isna() & merged_df[col2].isna()), diff_col] = 'DIFFERENT (value vs null)'
    
    # Generate timestamp for output file
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"detailed_diff_{timestamp}.csv"
    
    # Reorganize columns for better readability
    # First, key column
    new_cols = [key_col, 'Source']
    
    # Then group file1 and file2 columns with difference indicator for each field
    diff_cols = []
    
    for col in common_cols:
        if col != key_col:
            col1 = f"{col}_file1"
            col2 = f"{col}_file2"
            diff_col = f"{col}_diff"
            
            if col1 in merged_df.columns and col2 in merged_df.columns:
                new_cols.extend([col1, col2, diff_col])
                diff_cols.append(diff_col)
    
    # Add any remaining columns
    for col in merged_df.columns:
        if col not in new_cols:
            new_cols.append(col)
    
    # Reorder columns
    merged_df = merged_df[new_cols]
    
    # Save the comparison to a CSV file
    merged_df.to_csv(output_file, index=False)
    print(f"Comparison saved to: {output_file}")
    
    # Print summary statistics
    only_in_first = (merged_df['Source'] == f'Only in {os.path.basename(file1)}').sum()
    only_in_second = (merged_df['Source'] == f'Only in {os.path.basename(file2)}').sum()
    in_both = (merged_df['Source'] == 'In both files').sum()
    
    print("\n--- Summary ---")
    print(f"Records only in {file1}: {only_in_first}")
    print(f"Records only in {file2}: {only_in_second}")
    print(f"Records in both files: {in_both}")
    
    # Count the number of differences for matched records
    if in_both > 0:
        diff_counts = {}
        for diff_col in diff_cols:
            # Extract original column name
            orig_col = diff_col.replace('_diff', '')
            # Count non-empty difference indicators
            diff_count = (merged_df.loc[merged_df['Source'] == 'In both files', diff_col] != '').sum()
            diff_counts[orig_col] = diff_count
        
        print("\n--- Differences in matched records ---")
        for col, count in diff_counts.items():
            print(f"Field '{col}': {count} differences")
    
    # Also generate a summary file with differences only
    if in_both > 0:
        diff_only_df = merged_df.loc[merged_df['Source'] == 'In both files'].copy()
        
        # Flag if any differences exist
        has_diff = False
        for diff_col in diff_cols:
            if (diff_only_df[diff_col] != '').any():
                has_diff = True
                break
        
        if has_diff:
            # Filter to only include rows with at least one difference
            diff_mask = pd.Series(False, index=diff_only_df.index)
            for diff_col in diff_cols:
                diff_mask = diff_mask | (diff_only_df[diff_col] != '')
            
            diff_only_df = diff_only_df.loc[diff_mask]
            
            # Generate a name for the differences-only file
            diff_only_file = f"differences_{timestamp}.csv"
            diff_only_df.to_csv(diff_only_file, index=False)
            print(f"\nRows with differences saved to: {diff_only_file}")
            print(f"Number of rows with differences: {len(diff_only_df)}")
    
    # Generate a corrected CSV using file1 as base but taking file2 values for columns where they're more standardized
    # This is optional and would need customization for specific needs
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python detailed_csv_comparison.py file1.csv file2.csv [output.csv]")
        sys.exit(1)
    
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    
    output_file = None
    if len(sys.argv) >= 4:
        output_file = sys.argv[3]
    
    detailed_csv_comparison(file1, file2, output_file) 