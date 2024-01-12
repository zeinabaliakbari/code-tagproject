import csv
import pandas as pd
import xml.etree.ElementTree as ET
import pandas as pd
from pandas import json_normalize
import json
import os  
from pathlib import Path


def xml_to_csv(xml_file, csv_file):
    file_name = os.path.basename(xml_file)
    tree = ET.parse(xml_file)
    root = tree.getroot()
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
    #write result ro output file
   
    df_cleaned.to_csv(csv_file, index=False)
    if os.path.exists('XMLtoCSV0.csv'):
    # Delete the file
        os.remove('XMLtoCSV0.csv') 
   
            
def json_to_csv(json_file_path, csv_file_path):
    file_name = os.path.basename(json_file_path)

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
    df_cleaned.to_csv(csv_file_path, index=False)         
 

def replace_in_csv(csv_file, column_to_replace):
    # Specify the words we want to replace and their replacements
    word_replacements = { 
        "D": "@remove()",
        "DPI": "@hashptid(@SITEID,PatientID,10)",
        "DPN": "@integer(this,ptid,8)",
        "K": "@keep()",
        "SD": "@hashdate(this,PatientID)",
        "U2": "@hashuid(@UIDROOT, this)",
        "Z": "@empty()"
    }
    file_name, file_extension = os.path.splitext(os.path.basename(csv_file))
    output_file = file_name + "_replaced" + file_extension
    
    file= pd.read_csv(csv_file)
  
    file = file[file['TagComments'] != 'Private Creator'] # this is not Dicom element so remove records with this valus 
  
    # Sort csv file  based on 'TagID'
    file1_sorted = file.sort_values(by='TagID')
    file1_sorted.to_csv(csv_file, index=False) ### input file will be sorted 
    df=file1_sorted
    
    # No spaces or “'s” (apostrophes and 's') exist between words in the PrivateCreator column.
    df['TagComments'] = df['TagComments'].apply(lambda x: ''.join(x.split()))
    df['TagComments'] = df['TagComments'].apply(lambda x: x.replace("'s", '') if "'s" in x else x)

    # separate 'TagID' into two parts 
    df['Elem'] = df['TagID'].astype(str).str[-4:]
    df['Group'] = df['TagID'].astype(str).str[:-4]
    
    # Filter rows based on the condition
    condition = (df["Elem"] == 'yy00') | (df["Elem"] == '00yy') #***** non-valid records of PrivateCreator
    df = df[~condition]
    # replace 'yy' with '00'
    df.loc[:, 'Elem'] = df['Elem'].apply(lambda x: x.replace('yy', '00') if 'yy' in x else x)
 
    new_columns = {
    'Group': 'Group',
    'DependencyValue': 'PrivateCreator',
    'Elem': 'Elem',
    'TagComments': 'Name',
    'OperationType': 'Action',
   
    }
    # rename columns
    df = df.rename(columns=new_columns)[list(new_columns.values())]
   
     # intermediate  file 
    df.to_csv('file1_reordered.csv', index=False)
    input_file = 'file1_reordered.csv' ##****** I will delete this intermidate file 

   
 
    # Open the input CSV file for reading
    with open(input_file, 'r') as infile:
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
                 updated_row = [word_replacements[cell] if i == column_index and cell in word_replacements else cell + '_NOTFOUND' if i == column_index else cell for i, cell in enumerate(row)]
                 writer.writerow(updated_row)
    os.remove(input_file)    # delete the intermediate file        


 


if __name__ == "__main__":
    
    xml_file='teamplayMRclinicalUKER_xml.xml'
    json_file_path='SHS-base-profile_PL_json.json'
     
    xml_to_csv(xml_file, 'XMLtoCSV1.csv')
    json_to_csv(json_file_path, 'JSONtoCSV1.csv')
    # Create the final file by replacing the actions according to the CTP base profile
    replace_in_csv('XMLtoCSV1.csv' , 'Action')
    replace_in_csv('JSONtoCSV1.csv', 'Action')

