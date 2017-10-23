import requests
import json
import jsonschema
import pandas as pd 

from urlparse import urlparse
from urlparse import (uses_relative, uses_netloc, uses_params, urljoin)
from urllib import urlencode

def is_url(url):
    """ Check to see if the input is using one of the common URL protocols (http, git, ssh etc.) """

    valid_urls = set(uses_relative + uses_netloc + uses_params)
    valid_urls.discard('')
    return urlparse(url).scheme in valid_urls

class JsonProcess:
    """ Small class to read and process the inputted .JSON file
    
    Arguments:
        file_path -- type(str) Must be a valid URL or system file path to a .JSON file 

        schema_path -- type(str) Must be a valid URL or system file path to a .JSON file containing a JSON schema
                       default argument = 'default'

                       if 'default' then the URL to the schema found in the github FIRE repo will be used.
    """
    def __init__(self, file_path, schema_path = 'default'):

        if schema_path == 'default':
            schema_path = 'https://raw.githubusercontent.com/SuadeLabs/fire/master/v1-dev/derivative.json'

        if is_url(file_path):
            file_request = requests.get(schema_path)
            self.data = file_request.json()
        else:
            with open(file_path) as f:
                self.data = json.load(f)

        if is_url(schema_path):
            schema_request = requests.get(schema_path)
            self.schema = schema_request.json()
        else:
            with open(schema_path) as f:
                self.schema = json.load(f)
                
    def validate(self):
        """ Validates each line of the JSON 'data' array """
        for item in self.data['data']:
            try:
                jsonschema.validate(item, self.schema)
            except Exception as e:
                raise e
                
    def to_df(self):
        """ Converts JSON 'data' array to a pandas dataframe """
        self.validate()
        df = pd.DataFrame.from_records(self.data['data'])
        return df
