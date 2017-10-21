import pandas as pd
import numpy as np
import os 
import utils
import datetime as dt

class ExposureAtDefault:
    """ Class to handle the calculation of the Exposure of Default (EAD) for the given netting set 
    
    Arguments:
        data_path -- Must be a valid URL or system file path to a .JSON file (str)

        schema_path -- Must be a valid URL or system file path to a .JSON file containing a JSON schema (str), default = 'default'
                       if 'default' then the URL to the schema found in the github FIRE repo will be used.
    """

    def __init__(self, data_path, schema_path = 'default'):
        
        if schema_path == 'default':
            schema_path = 'https://raw.githubusercontent.com/SuadeLabs/fire/master/v1-dev/derivative.json'

        self.processor = utils.JsonProcess(data_path, schema_path)

        # Throws an exception if JSON data fails to match the schema.
        self.processor.validate() 

        # Converts the JSON data file to a dataframe. 
        # The resulting dataframe should be conceptually similar to that found on page 22 here: http://www.bis.org/publ/bcbs279.pdf 
        self.netting_set = self.processor.to_df()

    def replacement_cost(self):
        """ Calculates the replacment cost of the netting set as defined by paragraph 136 of http://www.bis.org/publ/bcbs279.pdf """
        market_values = self.netting_set['mtm_dirty'].values
        derivative_values = np.sum(market_values)
        return max(derivative_values, 0)

    def supervisory_duration(self):
        """ Calculates the supervisory duration parameter as defined by paragraph 157 of http://www.bis.org/publ/bcbs279.pdf """

        # Takes the contract dates and uses pandas to parse them into datetime objects
        start = pd.to_datetime(self.netting_set['start_date'].values)
        end = pd.to_datetime(self.netting_set['end_date'].values)
        current = pd.to_datetime(self.netting_set['date'].values)

        E = (end - start).days / 365.25
        S = (start - current).days / 365.25

        sup_duration = (np.exp(-0.05 * S) - np.exp(-0.05 * E)) / 0.05

        return sup_duration

    def adjusted_notional(self):

        sup_duration = self.supervisory_duration()
        return self.netting_set['notional_value'] * sup_duration

    def supervisory_delta(x):
        """ Calculates the supervisory delta adjustments as defined by paragraph 159 of http://www.bis.org/publ/bcbs279.pdf
            
            Note: This class method will be valid for non-options only. For future versions this method should be altered. 
                Alternatively, a child class could be created to handle the option specific behaviour. 
        """
        if x == 'fixed':
            return -1
        elif x == 'floating':
            return 1
        else:
            return np.nan
    
    def calculate(self):
        self.netting_set['adjusted_notional'] = self.adjusted_notional()
        self.netting_set['sup_delta'] = self.supervisory_delta()

        time_buckets = np.array([0, 1, 5, np.inf])

        effective_notional = {}
        # Create hedging sets based on currency_code
        for hedging_set in self.netting_set.groupby('currency_code'):
            hedging_set_name = hedging_set[0]
            effective_notional[set_name] = {} 

            # Maturity sets. Use a dict of dicts to track the maturity set for each hedging set.
            for time_bucket in self.netting_set.groupby(pd.cut(self.netting_set["maturity"], np.array([0, 1, 5, np.inf]))):
                maturity_set_name = time_bucket[0]
                effective_notional[set_name][maturity_set_name] = time_bucket[1]['adjusted_notional']
        
ExposureAtDefault('sample.json').replacement_cost()