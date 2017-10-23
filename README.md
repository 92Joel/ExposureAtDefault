# ExposureAtDefault
Program to calculate the Exposure at Default.

There are two main classes: ExposureAtDefault and JsonProcess. 

**JsonProcess**:

Description: Allows the user to input a .json file of derivatives data, validate it against the schema and output a dataframe.

Parameters: file_path - System path or URL to .json data file.
            schema_path - System path or URL to .json schema file. If none is input, will default to the schema found in the github FIRE repo.
            
**ExposureAtDefault**:

Description: Performs the Exposure at Default calculations

Parameters: netting_set - Pandas dataframe with columns as found here: https://raw.githubusercontent.com/SuadeLabs/fire/master/v1-dev/derivative.json

# Usage 

The simplest way to use the program is to use the included sample.json data file, process it with JsonProcess into a dataframe and input it into the ExposuresAtDefault class.

Example program: 

path = 'sample.json'

data_processor = JsonProcess(path)

data_processor.validate() 

netting_set = data_processor.to_df()

print ExposureAtDefault(netting_set).calculate()

# Testing 

One test case for the calculation has been provided using the sample IRS data found on page 22 here: http://www.bis.org/publ/bcbs279.pdf.

To test the JSON processing utitlity, multiple .JSON files have been created with minor modifications. The tests aim to check whether the program will correctly throw an error with incorrectly formatted data. 

To execute them, run python -m Suade.Tests.* from the root directory.

*: test_ead - Test just the Exposure at Default calculation class.

test_json - Test just the Json Processing class.

test_all - Test the above simultaneously.

# Requirements

* Python 2.7
* Pandas
* Numpy 
