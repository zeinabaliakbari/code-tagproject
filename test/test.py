import pandas as pd

# Assuming your CSV file is named 'your_file.csv' and has a column named 'ID'
file_path = 'JSONtoCSV_replaced.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Function to separate ID into tagid and groupid
def separate_id(id_value):
    tagid = id_value[-4:].replace('yy', '00')  # Last 4 characters with 'yy' replaced by '00'
    groupid = id_value[:-4]  # All characters except the last 4
    return tagid, groupid

# Apply the separation function to the 'ID' column and create new columns
df[['tagid', 'groupid']] = df['TagID'].apply(separate_id).apply(pd.Series)

# Save the modified DataFrame to a new CSV file
df.to_csv('output_file.csv', index=False)

# Display the modified DataFrame
print(df)
