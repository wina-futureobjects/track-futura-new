import pandas as pd
import sys

def generate_diff_csv(file1, file2, output_file):
    """
    Generate a CSV file that shows the differences between two CSV files.
    """
    print(f"Comparing {file1} and {file2}...")
    
    # Load files with pandas
    try:
        df1 = pd.read_csv(file1, encoding='utf-8', low_memory=False)
        df2 = pd.read_csv(file2, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        # Try another encoding if UTF-8 fails
        try:
            df1 = pd.read_csv(file1, encoding='latin1', low_memory=False)
            df2 = pd.read_csv(file2, encoding='latin1', low_memory=False)
        except Exception as e:
            print(f"Error reading files: {e}")
            return
    
    # Join the dataframes to find matching and non-matching rows
    if 'Post URL' in df1.columns and 'Post URL' in df2.columns:
        # Create copies to avoid SettingWithCopyWarning
        df1_temp = df1.copy()
        df2_temp = df2.copy()
        
        # Add source identifier
        df1_temp['Source'] = 'GE Tracker'
        df2_temp['Source'] = 'Generated Report'
        
        # Merge on Post URL to find common and different records
        merged = pd.merge(df1_temp, df2_temp, on='Post URL', how='outer', indicator=True, suffixes=('_file1', '_file2'))
        
        # Records only in first file
        only_in_first = merged[merged['_merge'] == 'left_only']
        # Records only in second file
        only_in_second = merged[merged['_merge'] == 'right_only']
        # Records in both files
        in_both = merged[merged['_merge'] == 'both']
        
        # Create output DataFrames
        # 1. Records in file1 but not in file2
        unique_to_file1 = df1[df1['Post URL'].isin(only_in_first['Post URL'])]
        unique_to_file1['Difference_Type'] = 'Only in GE Tracker'
        
        # 2. Records in file2 but not in file1 (should be none based on previous analysis)
        unique_to_file2 = df2[df2['Post URL'].isin(only_in_second['Post URL'])]
        unique_to_file2['Difference_Type'] = 'Only in Generated Report'
        
        # 3. Records that appear in both files but have differences
        # For all matching URLs, compare each column
        diff_records = []
        
        # Define columns to compare (all except Post URL which we know is the same)
        compare_cols = [col for col in df1.columns if col != 'Post URL']
        
        # Function to format difference for a cell
        def format_diff(val1, val2):
            if pd.isna(val1) and pd.isna(val2):
                return "Both NA"
            elif pd.isna(val1):
                return f"File1: NA | File2: {val2}"
            elif pd.isna(val2):
                return f"File1: {val1} | File2: NA"
            elif val1 != val2:
                return f"File1: {val1} | File2: {val2}"
            else:
                return str(val1)  # Same value
        
        # Process each matching URL to check for differences
        common_urls = in_both['Post URL'].unique()
        for url in common_urls:
            # Get the rows from each file with this URL
            row1 = df1[df1['Post URL'] == url].iloc[0]
            row2 = df2[df2['Post URL'] == url].iloc[0]
            
            # Check if any column has differences
            has_diff = False
            diff_cols = []
            for col in compare_cols:
                if col in row1 and col in row2:
                    val1 = row1[col]
                    val2 = row2[col]
                    # Handle special case for NaN comparison
                    if (pd.isna(val1) and pd.isna(val2)):
                        continue
                    elif pd.isna(val1) or pd.isna(val2) or val1 != val2:
                        has_diff = True
                        diff_cols.append(col)
            
            if has_diff:
                # Create a record with all columns from both files
                diff_record = {
                    'Post URL': url,
                    'Difference_Type': 'Field Mismatch',
                    'Mismatched_Fields': ', '.join(diff_cols)
                }
                
                # Add all columns from both files with clear labels
                for col in df1.columns:
                    if col in row1:
                        diff_record[f'{col}_GETracker'] = row1[col]
                
                for col in df2.columns:
                    if col in row2:
                        diff_record[f'{col}_Generated'] = row2[col]
                
                diff_records.append(diff_record)
        
        # Convert diff_records to DataFrame
        diff_df = pd.DataFrame(diff_records)
        
        # Combine all difference types into one DataFrame
        # First ensure they have the same columns
        for col in df1.columns:
            if col not in unique_to_file2.columns:
                unique_to_file2[col] = None
        
        for col in df2.columns:
            if col not in unique_to_file1.columns:
                unique_to_file1[col] = None
        
        # Concatenate the unique records dataframes
        all_uniques = pd.concat([unique_to_file1, unique_to_file2], ignore_index=True)
        
        # For the final output file:
        # 1. Records only in one file (with a type indicator)
        unique_diff_file = all_uniques[['Difference_Type'] + list(df1.columns)]
        
        # 2. Records with field mismatches
        mismatch_columns = ['Post URL', 'Difference_Type', 'Mismatched_Fields']
        # Add all other columns in a sorted way
        other_cols = sorted([col for col in diff_df.columns if col not in mismatch_columns])
        final_diff_df = diff_df[mismatch_columns + other_cols]
        
        # Save to CSV
        final_diff_df.to_csv(f"{output_file}_field_mismatches.csv", index=False)
        unique_diff_file.to_csv(f"{output_file}_unique_records.csv", index=False)
        
        print(f"Generated two difference files:")
        print(f"1. {output_file}_field_mismatches.csv - Records that exist in both files but have different field values")
        print(f"2. {output_file}_unique_records.csv - Records that exist in only one of the files")
        print(f"\nSummary:")
        print(f"- {len(unique_to_file1)} records only in {file1}")
        print(f"- {len(unique_to_file2)} records only in {file2}")
        print(f"- {len(diff_records)} records with field mismatches")
    else:
        print("Error: Both files must have a 'Post URL' column to compare.")
        return

if __name__ == "__main__":
    if len(sys.argv) < 4:
        file1 = "GE Tracker - FEB 2025 - WK06 - report.csv"
        file2 = "report_generated.csv"
        output_file = "differences"
    else:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        output_file = sys.argv[3]
    
    generate_diff_csv(file1, file2, output_file) 