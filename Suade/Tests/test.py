from exposure_at_default import ExposureAtDefault
from utils import JsonProcess
import pandas as pd 
import numpy as np
import numpy.testing
import unittest
import os

class TestExposureAtDefault(unittest.TestCase):
    """ Class to test the numerical calculations of each method used to calculate EAD are correct """
    def __init__(self, inp, out):
        super(TestExposureAtDefault, self).__init__() # Call the unittest.TestCase constructor
        self.input = inp
        self.output = out
        self.instance = ExposureAtDefault(self.input)
    
    def runTest(self):
        self.testRC()
        self.testSD()
        self.testAdjNotional()
        self.testStartEnd()
        self.testMaturity()
        self.testMF()
        self.testMultiplier()
        self.testAddon()
        self.testSupDelta()

    def testRC(self):
        expected_output = self.output['replacement_cost']
        func_output = self.instance.replacement_cost()
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

    def testSD(self):
        expected_output = self.output['supervisory_duration']
        func_output = np.round(self.instance.supervisory_duration())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)
    
    def testAdjNotional(self):
        expected_output = self.output['adjusted_notional']
        func_output = np.round(self.instance.adjusted_notional())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

    def testStartEnd(self):
        expected_output = self.output['start_end']
        func_output = np.round(self.instance.start_end_dates())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

    def testMaturity(self):
        expected_output = self.output['maturity']
        func_output = np.round(self.instance.maturity())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

    def testMF(self):
        expected_output = self.output['maturity_factor']
        func_output = np.round(self.instance.maturity_factor())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

    def testMultiplier(self):
        expected_output = self.output['multiplier']
        func_output = np.round(self.instance.multiplier())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

    def testAddon(self):
        expected_output = self.output['addon']
        func_output = np.round(self.instance.addon())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

    def testSupDelta(self):
        expected_output = self.output['sup_delta']
        func_output = np.round(self.instance.supervisory_delta())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

    def testCalculate(self):
        expected_output = self.output['EAD']
        func_output = np.round(self.instance.calculate())
        numpy.testing.assert_array_almost_equal(func_output, expected_output)

class TestJsonProcess(unittest.TestCase):
    """ Class to test various incorrect JSON files against the default schema"""
    def __init__(self, json_file):
        super(TestJsonProcess, self).__init__() # Call the unittest.TestCase constructor
        self.json_file = json_file
        self.instance = JsonProcess(json_file)

    def runTest(self):
        self.testValidateFails()

    def testValidateFails(self):
        try:
            self.instance.validate()
            self.fail('JSON file passed when an error was expected')
        except Exception:
            print 'exception'
            self.assertRaises(Exception)

def suite(known_values):
    json_files = os.listdir('tests')

    suite = unittest.TestSuite()
    suite.addTests(TestExposureAtDefault(x, y) for x, y in known_values)
    # suite.addTests(TestJsonProcess(x) for x in json_files)
    for x in json_files:
        full_file_path = os.path.abspath('tests/' + x)
        suite.addTest(TestJsonProcess(full_file_path))
    return suite

input1 = pd.DataFrame({
"id": ["swap_1", "swap_2"],
"date": ["2009-01-17T00:00:00Z", "2015-01-17T00:00:00Z"],
"asset_class": ["ir", "ir"],
"currency_code": ["USD", "USD"],
"end_date": ["2019-01-17T00:00:00Z", "2019-01-17T00:00:00Z"],
"mtm_dirty": [30, -20],
"notional_amount": [10000, 10000],
"payment_type": ["fixed", "floating"],
"receive_type": ["floating", "fixed"],
"start_date": ["2009-01-17T00:00:00Z", "2015-01-17T00:00:00Z"],
"type": ["vanilla_swap", "vanilla_swap"],
"trade_date": ["2009-01-10T00:00:00Z", "2015-01-10T00:00:00Z"],
"value_date": ["2009-01-17T00:00:00Z", "2009-01-17T00:00:00Z"]
})

output1 = {'replacement_cost': 10,
           'supervisory_duration': np.array([8.,4.]),
           'adjusted_notional': np.array([78686., 36254.]),
           'start_end': np.array([[0., 0.], [10., 4.]]),             
           'maturity': np.array([ 10., 4.]), 
           'maturity_factor': np.array([1., 1.]),
           'multiplier': 1, 
           'addon': 296,
           'sup_delta': np.array([1, -1]),
           'EAD': 429
           }

known_values = [(input1, output1)]

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite(known_values))