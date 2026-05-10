import pandas as pd

# Load CSV
file_path = "./Dataset/AQI_dataset.csv"
df = pd.read_csv(file_path)

# Check original shape
print("Original Shape:", df.shape)

# Remove only fully empty rows
df.dropna(how='all', inplace=True)

# Remove unwanted columns
df.drop(['pm25', 'pm10', 'no2', 'so2', 'o3', 'Unnamed: 5'],
        axis=1,
        inplace=True)

# Check remaining data
print("Final Shape:", df.shape)

# Preview
print(df.head())

# Export
df.to_csv("cleaned_dataset.csv", index=False)

print("CSV exported successfully")