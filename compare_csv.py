import csv
import pandas as pd
import sys

def compare_csv_files(file1, file2):
    """
    Compare two CSV files and report the differences
    """
    print(f"Comparing {file1} and {file2}...")
    
    # Load files with pandas
    try:
        df1 = pd.read_csv(file1, encoding='utf-8')
        df2 = pd.read_csv(file2, encoding='utf-8')
    except UnicodeDecodeError:
        # Try another encoding if UTF-8 fails
        try:
            df1 = pd.read_csv(file1, encoding='latin1')
            df2 = pd.read_csv(file2, encoding='latin1')
        except Exception as e:
            print(f"Error reading files: {e}")
            return
    
    # Basic file statistics
    print("\n--- Basic Statistics ---")
    print(f"File 1 ({file1}) - Rows: {len(df1)}, Columns: {len(df1.columns)}")
    print(f"File 2 ({file2}) - Rows: {len(df2)}, Columns: {len(df2.columns)}")
    
    # Compare columns
    print("\n--- Column Comparison ---")
    cols1 = set(df1.columns)
    cols2 = set(df2.columns)
    
    if cols1 == cols2:
        print("Both files have the same columns.")
    else:
        print("Column differences:")
        print(f"Columns only in {file1}: {cols1 - cols2}")
        print(f"Columns only in {file2}: {cols2 - cols1}")
    
    # Compare content based on common columns
    common_cols = list(cols1.intersection(cols2))
    
    # Check if there's a common identifier column to merge on
    # For this specific case, we know URL might be a good candidate
    if 'Post URL' in common_cols:
        merge_col = 'Post URL'
        print(f"\n--- Content Comparison based on {merge_col} ---")
        
        # Join the dataframes to find matching and non-matching rows
        merged = pd.merge(df1, df2, on=merge_col, how='outer', indicator=True)
        
        # Count matches and differences
        only_in_first = merged[merged['_merge'] == 'left_only']
        only_in_second = merged[merged['_merge'] == 'right_only']
        in_both = merged[merged['_merge'] == 'both']
        
        print(f"Records only in {file1}: {len(only_in_first)}")
        print(f"Records only in {file2}: {len(only_in_second)}")
        print(f"Records in both files: {len(in_both)}")
        
        if len(in_both) > 0:
            # For matching URLs, check if other fields match
            print("\n--- Field Comparison for Common Records ---")
            
            # Construct comparison columns
            comparison_cols = []
            for col in common_cols:
                if col != merge_col:
                    col_x = f"{col}_x"  # From first file
                    col_y = f"{col}_y"  # From second file
                    if col_x in in_both.columns and col_y in in_both.columns:
                        comparison_cols.append((col, col_x, col_y))
            
            # Count mismatches for each field
            for col_name, col_x, col_y in comparison_cols:
                # Compare values with safe handling for different types
                try:
                    mismatches = (in_both[col_x] != in_both[col_y]).sum()
                    print(f"Field '{col_name}' has {mismatches} mismatches")
                except Exception as e:
                    print(f"Error comparing '{col_name}': {e}")
    
    # Platform type distribution comparison
    if 'Platform Type' in common_cols:
        print("\n--- Platform Type Distribution ---")
        print(f"File 1 ({file1}):")
        print(df1['Platform Type'].value_counts())
        
        print(f"\nFile 2 ({file2}):")
        print(df2['Platform Type'].value_counts())
    
    # Date range comparison
    if 'Posting Date' in common_cols:
        print("\n--- Date Range Comparison ---")
        print(f"File 1 date range: {df1['Posting Date'].min()} to {df1['Posting Date'].max()}")
        print(f"File 2 date range: {df2['Posting Date'].min()} to {df2['Posting Date'].max()}")
    
    # S/N column format
    if 'S/N' in common_cols:
        print("\n--- S/N Column Format ---")
        print(f"File 1 S/N format: {df1['S/N'].head(5).tolist()}")
        print(f"File 2 S/N format: {df2['S/N'].head(5).tolist()}")
    
    # Sample of different records
    print("\n--- Sample Differences ---")
    # Display sample rows from each file
    print(f"Sample from {file1} (first 3 rows):")
    sample_cols = ['Name', 'IAC No.', 'Posting Date', 'Platform Type']
    safe_cols1 = [col for col in sample_cols if col in df1.columns]
    if safe_cols1:
        print(df1[safe_cols1].head(3).to_string())
    
    print(f"\nSample from {file2} (first 3 rows):")
    safe_cols2 = [col for col in sample_cols if col in df2.columns]
    if safe_cols2:
        print(df2[safe_cols2].head(3).to_string())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        file1 = "GE Tracker - FEB 2025 - WK06 - report.csv"
        file2 = "report_generated.csv"
    else:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
    
    compare_csv_files(file1, file2) 