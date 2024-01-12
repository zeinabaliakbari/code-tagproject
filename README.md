# Create a dictionary to convert different DICOM profiles into each other

## Project Overview

this project has two parts include:
1.  converting files with formats XML and json to CSV 
2. creating a dictionary to make csv file into specif style as a Dicom Anonymization profile
  

## Methodology


Convert XML to CSV :

Reads an XML file .
Converts the XML data to a CSV file (XMLtoCSV.csv).
Filters out specific columns ('DependencyID') and saves the cleaned CSV file.

Convert JSON to CSV:

Reads a JSON file .
Flattens the nested "Minimization" array and converts the JSON data to a CSV file (JSONtoCSV.csv).
Filters out specific columns and saves the cleaned CSV file.

Replace Values in CSV:

Replaces values in a specified column ('Action') of the generated CSV files (XMLtoCSV.csv and JSONtoCSV.csv) based on a predefined dictionary of replacements.
Removes spaces between words in the 'TagComments' column and removes specific records based on distination style.
Sorts the CSV file based on the 'TagID' column.
Writes the cleaned and sorted CSV file to 'file1_reordered.csv'.
Applies additional transformations.
Renames columns and saves the final result to a new CSV file with '_replaced' appended to the original filename (e.g., XMLtoCSV_replaced.csv).
