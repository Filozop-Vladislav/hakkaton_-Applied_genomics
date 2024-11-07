import os
import pandas as pd
import re

def process_cyp2b6_files(root_directory):
    data = []  # List to store data from all files

    # Traverse through each folder in the specified directory
    for pharma_dir in os.listdir(root_directory):
        # Check that the folder name ends with .MGI.Pharma
        match = re.match(r'^(\d+)\.MGI\.Pharma$', pharma_dir)
        if match:
            pharma_path = os.path.join(root_directory, pharma_dir)
            numeric_prefix = match.group(1)  # Extract the numeric part

            # Check that this is a directory
            if os.path.isdir(pharma_path):
                # Look for the .MGI.StellarPGx folder
                stellar_pgx_dir = None
                for subdir in os.listdir(pharma_path):
                    if re.match(r'^\d+\.MGI\.StellarPGx$', subdir):
                        stellar_pgx_dir = os.path.join(pharma_path, subdir)
                        break
                
                # If the .MGI.StellarPGx folder is found
                if stellar_pgx_dir and os.path.isdir(stellar_pgx_dir):
                    # Iterate through all files in the .MGI.StellarPGx folder
                    for filename in os.listdir(stellar_pgx_dir):
                        # Process only files containing 'cyp2b6' in their name
                        if "cyp2b6" in filename and filename.endswith(".alleles"):
                            filepath = os.path.join(stellar_pgx_dir, filename)
                            
                            # Extract the gene name from the filename
                            gene_match = re.search(r'_([a-zA-Z0-9]+)\.alleles$', filename)
                            gene_name = gene_match.group(1) if gene_match else "Unknown"

                            # Read the .alleles file
                            with open(filepath, 'r') as file:
                                content = file.readlines()

                                # Search for "Result:" lines
                                result_status = None
                                for i, line in enumerate(content):
                                    if "Result:" in line:
                                        # Check if the next line contains the result
                                        if i + 1 < len(content):
                                            result_status = content[i + 1].strip()
                                            break
                                
                                # If result status is found, add information to the list
                                if result_status:
                                    data.append({
                                        "File": numeric_prefix,  # Store only the numeric part
                                        "Result": result_status,
                                        "Gene": gene_name  # Store the gene name
                                    })

    # Create a unified DataFrame and save it as a CSV file
    if data:
        result_df = pd.DataFrame(data)
        output_file = os.path.join(root_directory, "gavno.csv")
        result_df.to_csv(output_file, index=False)
        print(f"Saved the final output to: {output_file}")
    else:
        print("No suitable files with 'Result:' found.")

# Specify the path to your folder
process_cyp2b6_files(r"C:\MyPythonWorks\Pharma")

