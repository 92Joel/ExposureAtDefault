from exposure_at_default import ExposureAtDefault
from utils import JsonProcess

import pandas as pd 
import numpy as np
import os

src_path = os.path.dirname(os.path.abspath(__file__)) # Absolute path of source file

if os.name == 'posix':
    path = src_path + '/Sample_Data/sample.json' # Linux path

if os.name == 'nt':
    path = src_path + '\Sample_Data\sample.json' # Windows path

data_processor = JsonProcess(path)

# Throws an exception if JSON data fails to match the schema.
data_processor.validate() 

# Converts the JSON data file to a dataframe. 
# The resulting dataframe should be conceptually similar to that found on page 22 here: http://www.bis.org/publ/bcbs279.pdf 
netting_set = data_processor.to_df()

print (ExposureAtDefault(netting_set).calculate())