import os
import pandas as pd

print("Creating PDBbind mini dataset...")

# Using the absolute path and matching your exact folder spelling
dataset_folder = r"C:\Users\Samiullah\Documents\FYP\backend\dataset\pbdbind"

try:
    # This reads all the folder names (like 1a30, 1bcu) inside the pbdbind directory
    folders = [f for f in os.listdir(dataset_folder) if os.path.isdir(os.path.join(dataset_folder, f))]
    
    # Create a dataframe and save it directly to the backend folder
    df = pd.DataFrame({"pdb_id": folders})
    
    output_path = r"C:\Users\Samiullah\Documents\FYP\backend\pdbbind_mini.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Done! pdbbind_mini.csv created with {len(folders)} entries.")
    
except FileNotFoundError:
    print(f"Error: Could not find the folder at {dataset_folder}. Check the spelling!")