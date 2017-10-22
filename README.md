# ExposureAtDefault
Program to calculate the Exposure at Default.

There are two main classes: ExposureAtDefault and JsonProcess. 

JsonProcess:
Description: Allows the user to input a .json file of derivatives data, validate it against the schema and output a dataframe.

Parameters: file_path - System path or URL to .json data file.
            schema_path - System path or URL to .json schema file. If none is input, will default to the schema found in the github FIRE repo.
            
ExposureAtDefault:
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

# Requirements

Python 2.7
Pandas
Numpy 
