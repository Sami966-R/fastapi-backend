import pandas as pd

print("Creating ChEMBL mini dataset...")

# Notice the path now goes INTO the folder to grab the actual file!
dataset_path = r"C:\Users\Samiullah\Documents\FYP\backend\dataset\chembl_36_chemreps.txt\chembl_36_chemreps.txt"

df = pd.read_csv(dataset_path, sep="\t", nrows=5000)

output_path = r"C:\Users\Samiullah\Documents\FYP\backend\chembl_mini.csv"
df.to_csv(output_path, index=False)

print("Done! chembl_mini.csv has been created.")