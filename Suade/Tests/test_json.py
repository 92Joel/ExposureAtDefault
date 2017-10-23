from ..utils import JsonProcess
import unittest
import os

class TestJsonProcess(unittest.TestCase):
    """ Class to test various incorrect JSON files against the default schema"""
    
    def __init__(self, json_file):
        super(TestJsonProcess, self).__init__() # Call the unittest.TestCase constructor
        self.json_file = json_file
        self.instance = JsonProcess(json_file)

    def runTest(self):
        self.testValidateFails()
        self.testToDf()

    def testValidateFails(self):
        failed = False
        try:
            self.instance.validate()
            failed = True # Fail the test if the JSON incorrectly passes the validate() stage. 
        except Exception:
            self.assertRaises(Exception)

        if failed:
            self.fail('JSON file passed when an error was expected')
    
    def testToDf(self):
        failed = False
        try:
            self.instance.to_df()
            failed = True # Fail the test if the JSON incorrectly passes the validate() stage. 
        except Exception:
            self.assertRaises(Exception)

        if failed:
            self.fail('JSON file was successfully converted to a DataFrame when a fail was expected.')

def suite():
    src_path = os.path.dirname(os.path.abspath(__file__)) # Absolute path of source file
    json_files = os.listdir(src_path + '/Incorrect_JSONS')

    suite = unittest.TestSuite()
    for x in json_files:
        full_file_path = os.path.abspath(src_path + '/Incorrect_JSONS/' + x)
        suite.addTest(TestJsonProcess(full_file_path))
    return suite

# if __name__ == '__main__':
unittest.TextTestRunner().run(suite())