import os
import pandas as pd
import re

def remove_ansi_codes(text):
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

def process_res_files_in_pharma_directories(root_directory):
    data = []  # List to store data from all .res files

    # Iterate over each directory in the specified root directory
    for pharma_dir in os.listdir(root_directory):
        if re.match(r'^\d+\.MGI\.Pharma$', pharma_dir):
            pharma_path = os.path.join(root_directory, pharma_dir)
            
            if os.path.isdir(pharma_path):
                # Search for the .MGI.aldy folder
                aldy_dirs = [d for d in os.listdir(pharma_path) if d.endswith(".MGI.aldy")]
                
                for aldy_dir in aldy_dirs:
                    aldy_path = os.path.join(pharma_path, aldy_dir)
                    
                    # Check each .res file in the .MGI.aldy folder
                    for filename in os.listdir(aldy_path):
                        if filename.endswith(".res"):
                            filepath_res = os.path.join(aldy_path, filename)
                            filepath_out = filepath_res.replace(".res", ".out")  # Corresponding .out file name
                            
                            if not os.path.exists(filepath_out):
                                print(f".out file missing for {filename}")
                                continue
                            
                            # Extract 'human' and 'gen' information from the file name
                            parts = filename.split(".")
                            human = parts[0]
                            gen = parts[1]

                            # Read data from .res file
                            try:
                                df = pd.read_csv(filepath_res, sep="\t")
                                
                                if "Type" in df.columns:
                                    type_values = df["Type"]
                                else:
                                    print(f"'Type' column not found in {filename}")
                                    continue
                            except Exception as e:
                                print(f"Error processing file {filename}: {e}")
                                continue
                            
                            # Extract values for "Best ... star-alleles" and "Estimated activity for" from .out file
                            activity1 = activity2 = aoa = None
                            try:
                                with open(filepath_out, 'r') as file:
                                    for line in file:
                                        line = remove_ansi_codes(line).strip()
                                        
                                        # Find "Estimated activity for *1"
                                        if line.startswith("Estimated activity for *1:") and activity1 is None:
                                            activity1 = line.split(":", 1)[1].strip()
                                        
                                        # Find "Estimated activity for *2"
                                        elif line.startswith("Estimated activity for *2:") and activity2 is None:
                                            activity2 = line.split(":", 1)[1].strip()
                                        
                                        # Look for "Best ... star-alleles" line and capture allele info
                                        if "Best" in line and "star-alleles" in line:
                                            match = re.search(r"Best .*? star-alleles.*?:\s+\d+:\s+([^\(]+)", line)
                                            if match:
                                                aoa = match.group(1).strip()  # Capture allele info like "*1 / *1"

                                    if not activity1:
                                        print(f"'Estimated activity for *1' not found in {filepath_out}")
                                    if not activity2:
                                        print(f"'Estimated activity for *2' not found in {filepath_out}")
                            except Exception as e:
                                print(f"Error reading .out file {filepath_out}: {e}")
                                continue
                            
                            # Verify required columns in .res file and store results in 'data' list
                            if all(column in df.columns for column in ["Effect", "Location", "Allele"]):
                                for idx, row in df.iterrows():
                                    data.append({
                                        "human": human,
                                        "gen": gen,
                                        "Type": type_values[idx] if idx < len(type_values) else None,
                                        "Effect": row["Effect"],
                                        "Location": row["Location"],
                                        "Allele": row["Allele"],
                                        "Estimated activity for *1": activity1,
                                        "Estimated activity for *2": activity2,
                                        "aoa": aoa  # Add 'aoa' column
                                    })
                            else:
                                print(f"Skipped file {filename}: required columns missing")

    # Create final table and save as CSV
    if data:
        result_df = pd.DataFrame(data)
        output_file = os.path.join(root_directory, "aldy.csv")
        result_df.to_csv(output_file, index=False)
        print(f"Saved final file: {output_file}")

# Example usage
root_directory = r"C:\MyPythonWorks\Pharma"  # Specify root directory path
process_res_files_in_pharma_directories(root_directory)
