
import csv
import pandas as pd
import xml.etree.ElementTree as ET
import pandas as pd
from pandas import json_normalize
import json
import os  
from pathlib import Path


def xml_to_csv(xml_file, csv_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Assuming each record is represented by an element named 'record'
    records = root.findall('tag')

    with open('XMLtoCSV0.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)

        # Write header based on all unique XML element names
        header = list(set(element.tag for record in records for element in record))
        csv_writer.writerow(header)

        for record in records:
            # Extract data from XML elements and write to CSV rows
            row = [record.find(element).text if record.find(element) is not None else '' for element in header]
            csv_writer.writerow(row)
             
    # remove null column
    df = pd.read_csv('XMLtoCSV0.csv',encoding='unicode_escape') 
    columns_to_remove = ['DependencyID'] 
    df_cleaned = df.drop(columns=columns_to_remove)
    df_cleaned['Source'] = 'teamplayMRclinicalUKER_xml'
     #write result ro output file
    df_cleaned.to_csv(csv_file, index=False)
    if os.path.exists('XMLtoCSV0.csv'):
    # Delete the file
        os.remove('XMLtoCSV0.csv') 
   
            
def json_to_csv(json_file_path, csv_file_path):
     

    # Read JSON data from the file
    with open(json_file_path) as f:
        json_data = json.load(f)

    # Flatten the nested "Minimization" array
    minimization_df = json_normalize(json_data, 'Minimization', errors='ignore')

    # Remove the "Minimization" key from the original data
    json_data.pop('Minimization', None)

    # Convert the remaining attributes to a DataFrame
    main_df = pd.DataFrame([json_data])

    # Concatenate the DataFrames
    result_df = pd.concat([main_df, minimization_df], axis=1)  
    # remove null columns 
    columns_to_remove = ['ProfileName', 'description', 'Version', 'MapJsonList', 'Enrichment']
    df_cleaned = result_df.drop(columns=columns_to_remove)
    #write result ro output file
    df_cleaned['Source'] = 'SHS-base-profile_PL_json'
    df_cleaned.to_csv(csv_file_path, index=False)         
            


def separate_id(id_value):
    
    tagid = id_value[-4:].replace('yy', '00')  # Last 4 characters with 'yy' replaced by '00'
    groupid = id_value[:-4]  # All characters except the last 4
    return tagid, groupid

def replace_in_csv(csv_file, column_to_replace):
    input_file = csv_file # keep input file without any change
    # Specify the words you want to replace and their replacements
    word_replacements = {
        "D": "@remove()",
        "DPI": "@hashptid(@SITEID,PatientID,10)",
        "DPN": "@integer(this,ptid,8)",
        "K": "@keep()",
        "SD": "@hashdate(this,PatientID)",
        "U2": "@hashuid(@UIDROOT, this)",
        "Z": "@empty()",
    }
    
    file_name, file_extension = os.path.splitext(os.path.basename(csv_file))
    output_file = file_name + "_replaced" + file_extension
    
    file= pd.read_csv(input_file)
        
    #ctp : Group	PrivateCreator	Elem	Name	Action
    sort_column = 'TagID'
    df = file.sort_values(by=sort_column)#sort TAGID
   # df[sort_column] = df[sort_column].apply(lambda x: x.replace('yy', '00') if 'yy' in x else x)
    df['Elem'] = df[ sort_column].astype(str).str[-4:]
    df['Group'] = df[ sort_column].astype(str).str[:-4]
    
   # df[['Elem', 'Group']] = df['TagID'].apply(separate_id).apply(pd.Series)# use separate_id function to separate 
    new_columns = {
    'Group': 'Group',
    'DependencyValue': 'PrivateCreator',
    'Elem': 'Elem',
    'TagComments': 'Name',
    'OperationType': 'Action',
    'Source': 'Source'
    }
    df = df.rename(columns=new_columns)[list(new_columns.values())]
    
   # df['Group'] = df['Group'].astype(str).replace(r'^0+', '', regex=True)
   # df['Elem'] = df['Elem'].astype(str).replace(r'^0+', '', regex=True)
    
    
    df.to_csv(output_file, index=False)

 # replace Action base on word_replacements
    with open(output_file, 'r') as infile:
        # Create a CSV reader
        reader = csv.reader(infile)
        
        # Read the header if your CSV has one
        header = next(reader, None)
        
        # Find the index of the specified column
        column_index = header.index(column_to_replace) if header and column_to_replace in header else None

        # Check if the specified column exists in the header
        if column_index is None:
            raise ValueError(f"Column '{column_to_replace}' not found in the CSV file.")

        # Open the output CSV file for writing
        with open(output_file, 'w', newline='') as outfile:
            # Create a CSV writer
            writer = csv.writer(outfile)
            
            # Write the header if it exists
            if header:
                writer.writerow(header)
            
            # Iterate through each row in the input CSV
            for row in reader:           
                 updated_row = [word_replacements[cell] if cell in word_replacements else cell + '_NOTFOUND' if i == column_index else cell for i, cell in enumerate(row)]
                 writer.writerow(updated_row)


 

def compare_csv_files(file1_path, file2_path, output_path='differences.csv'):
     
    file_name1, file_extension1 = os.path.splitext(os.path.basename(file1_path))
    suffixes1 =   "_" + file_name1
 
    file_name2, file_extension2 = os.path.splitext(os.path.basename(file2_path))
    suffixes2 =   "_" + file_name2
    # Read the CSV files
    file1 = pd.read_csv(file1_path)
    file2 = pd.read_csv(file2_path)
    

    # Merge files on the 'ID' column
    #meaningful column
    operationtype1='OperationType_'+file_name1
    operationtype2='OperationType_'+file_name2
     #meaningful column
    merged = pd.merge(file1, file2, on='TagID', how='outer', suffixes=(suffixes1, suffixes2))
     # Identify rows where the status is different and both statuses are not NaN
    differences = merged[(merged[operationtype1] != merged[operationtype2]) & (~merged[operationtype1].isnull()) & (~merged[operationtype2].isnull())]


    # Save differences to CSV with specific columns
    differences[['TagID',operationtype1, operationtype2]].to_csv(output_path, index=False)
    print(f"Differences saved to {output_path}")

    # Save rows only in file1 to CSV
 
    #only_in_file1 
    filename1='only_in_'+file_name1+file_extension1
    only_in_file1 = merged[merged[operationtype2].isnull()]
    only_in_file1[['TagID', operationtype1]].to_csv(filename1, index=False)
    print("Rows only in file1 saved to only_in_file1.csv")

    # Rows only in file2
    filename2='only_in_'+file_name2+file_extension2
    only_in_file2 = merged[merged[operationtype1].isnull()]
    only_in_file2[['TagID', operationtype2]].to_csv(filename2, index=False)
    print("Rows only in file2 saved to only_in_file2.csv")
    
 
# Example usage:


    
if __name__ == "__main__":
    xml_file='PPA.xml'
    json_file_path='shs.json'
     
    
    xml_to_csv(xml_file, 'XMLtoCSV.csv')
    json_to_csv(json_file_path, 'JSONtoCSV.csv')
     
    replace_in_csv('XMLtoCSV.csv' , 'Action')
    replace_in_csv('JSONtoCSV.csv', 'Action')
    
    #df = pd.read_csv('Profile.csv')
    #df = df.drop('Source', axis=1)
    #df.to_csv('Profile.csv', index=False)
    # compare_csv_files('XMLtoCSV_replaced.csv', 'JSONtoCSV_replaced.csv')
