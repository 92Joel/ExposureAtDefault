import pandas as pd
import numpy as np
import os 
import utils
import datetime as dt

class ExposureAtDefault:
    """ 
    Class to handle the calculation of the Exposure of Default (EAD) for the given netting set 
    
    Arguments:
        data_path -- type (str) Must be a valid URL or system file path to a .JSON file 

        schema_path -- type (str) Must be a valid URL or system file path to a .JSON file containing a JSON schema, default = 'default'
                       if 'default' then the URL to the schema found in the github FIRE repo will be used.
    """

    def __init__(self, netting_set):
        
        self.netting_set = netting_set
        # Add additional columns to our table of data which we need for the final calculation.
        self.netting_set['adjusted_notional'] = self.adjusted_notional()
        self.netting_set['sup_delta'] = self.netting_set['receive_type'].apply(lambda x: self.supervisory_delta(x))
        self.netting_set['maturity'] = self.maturity()
        self.netting_set['mf'] = self.maturity_factor()

    def replacement_cost(self):
        """ Calculates the replacment cost of the netting set as defined by paragraph 136 of http://www.bis.org/publ/bcbs279.pdf """
        market_values = self.netting_set['mtm_dirty'].values
        derivative_values = np.sum(market_values)
        return max(derivative_values, 0)

    def supervisory_duration(self):
        """ Calculates the supervisory duration parameter as defined by paragraph 157 of http://www.bis.org/publ/bcbs279.pdf """
        S, E = self.start_end_dates()
        sup_duration = (np.exp(-0.05 * S) - np.exp(-0.05 * E)) / 0.05

        return sup_duration.values

    def adjusted_notional(self):

        sup_duration = self.supervisory_duration()
        adj_notional = self.netting_set['notional_amount'] * sup_duration
        return adj_notional.values

    def supervisory_delta(self, x):
        """ 
        Calculates the supervisory delta adjustments as defined by paragraph 159 of http://www.bis.org/publ/bcbs279.pdf
            
        Note: This class method will be valid for non-options only. For future versions this method should be altered. 
            Alternatively, a child class could be created to handle the option specific behaviour. 

        """
        if x == 'fixed':
            return -1
        elif x == 'floating':
            return 1
        else:
            return np.nan
    
    def start_end_dates(self):
        """ Calculates S and E as defined in paragraph 157 of http://www.bis.org/publ/bcbs279.pdf """

        # Takes the contract dates and uses pandas to parse them into datetime objects
        start = pd.to_datetime(self.netting_set['start_date'].values)
        end = pd.to_datetime(self.netting_set['end_date'].values)
        current = pd.to_datetime(self.netting_set['date'].values)

        E = (end - start).days / 365.25
        S = (start - current).days / 365.25
        S = np.array( map(lambda x: max(x, 0), S) ) # Convert negative start dates to 0

        return S,E

    def maturity(self):
        """ Calculates the maturity of the contract in years """
        end = pd.to_datetime(self.netting_set['end_date'].values)
        current = pd.to_datetime(self.netting_set['date'].values)

        maturity = (end - current).days / 365.25
        return maturity.values

    def maturity_factor(self):
        """ Calculates MF as defined in paragraph 164 of http://www.bis.org/publ/bcbs279.pdf """

        maturity = self.maturity() # Time to maturity
        mf = np.sqrt(map(lambda x: min(x, 1), maturity))
        return mf 

    def effective_notionals(self):
        
        time_buckets = np.array([0, 1, 5, np.inf]) # Defines three time buckets: [0 < 1], [1 < 5], [> 5]

        D = {} # Dict of dicts to hold the effective notionals for each maturity bucket per hedging set.

        # Create hedging sets based on currency_code
        for hedging_set in self.netting_set.groupby('currency_code'):

            hedging_set_name, hedging_set_df = hedging_set[0], hedging_set[1]
            D[hedging_set_name] = {} 

            # Group each hedging set by maturity range
            maturity_buckets = hedging_set_df.groupby(pd.cut(hedging_set_df["maturity"], time_buckets)) 
            
            for i, time_bucket in enumerate(maturity_buckets):
                maturity_set_name, maturity_set_df = time_bucket[0], time_bucket[1]

                notional = maturity_set_df['adjusted_notional'] * maturity_set_df['sup_delta'] * maturity_set_df['mf']
                if notional.empty:
                    notional = pd.Series(0)
                D[hedging_set_name][i] = notional.values

        return D
    
    def multiplier(self):
        """ Calculates the multiplier as defined in paragraph 148 of http://www.bis.org/publ/bcbs279.pdf """

        floor = 0.0
        addon = self.addon()

        market_values = self.netting_set['mtm_dirty'].values
        derivative_values = np.sum(market_values)

        num = derivative_values
        denom = 2 * (1 - floor) * addon
        exponent = np.exp(num / denom)

        multiplier = floor + (1 - floor) * exponent
        multiplier = min(1, multiplier)
        return multiplier

    def addon(self):
        """ Calculates the add on as defined by paragraphs 166-169 in http://www.bis.org/publ/bcbs279.pdf """
        
        D = self.effective_notionals()

        hedging_addons = {} # Dict to hold the addon per hedging set
        for hedging_set in D:
            notionals = D[hedging_set] # Get the notionals for the 3 maturity buckets in each hedging set
            value = np.sqrt((notionals[0] ** 2) + (notionals[1] ** 2) + (notionals[2] ** 2) + 1.4 * notionals[1] * notionals[2] + 0.6 * notionals[0] * notionals[2])
            hedging_addons[hedging_set] = 0.005 * value

        addon = np.sum(hedging_addons.values())
        return addon   

    def calculate(self):
        """ Calculates the Exposure at Default as defined in paragraph 128 of http://www.bis.org/publ/bcbs279.pdf"""

        agg_addon = self.addon()
        multiplier = self.multiplier()
        rc = self.replacement_cost()
        alpha = 1.4
        exposure_at_default = alpha * (rc + (multiplier * agg_addon))

        return exposure_at_default     

