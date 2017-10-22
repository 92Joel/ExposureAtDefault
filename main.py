from exposure_at_default import ExposureAtDefault
from utils import JsonProcess

import pandas as pd 
import numpy as np

path = 'sample.json'
data_processor = JsonProcess(path)

# Throws an exception if JSON data fails to match the schema.
data_processor.validate() 

# Converts the JSON data file to a dataframe. 
# The resulting dataframe should be conceptually similar to that found on page 22 here: http://www.bis.org/publ/bcbs279.pdf 
netting_set = data_processor.to_df()

print (ExposureAtDefault(netting_set).calculate())