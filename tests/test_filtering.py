# Tests for the filtering process
# Created by: Benoit Cote (June, 2022)

# Import Python modules
import numpy  as np

# Import Interface tools
from Interface import read_data_file

# TestFiltering class
# ===================
class TestFiltering:
    """Class that tests the filtering functionalities. """

    # Instantiate the reading scripts and setting root folder
    rdf = read_data_file.read_data_file(root_path="./tests/data/")

    # Read the test-case file to be filtered
    d = rdf.read_file("file_8.txt", "file_8_structure.txt")

    # Test filter #1
    # ==============
    def test_filter_1(self):
        '''Testing the = operator. '''

        # Compare filtered data with the raw data
        quantities = "label"
        conditions = ["number = 0.100445"]
        expected = [["label1"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["right", "string"]
        conditions = ["number = -9.0e-1"]
        expected = [[[3,4,5,7,8],"Niak6^^ a"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["label", "right"]
        conditions = ["left = 3"]
        expected = [["label1",[3]], ["label2",[35]], ["label3",[5]], ["label4",[0.4]]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["string"]
        conditions = ["number = 35", "right = 58"]
        expected = [["AokE haaa"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["left"]
        conditions = ["right = 5"]
        expected = [[[5]], [[3]]]
        self.__compare_filter(quantities, conditions, expected)


    # Test filter #2
    # ==============
    def test_filter_2(self):
        '''Testing the != operator. '''

        # Compare filtered data with the raw data
        quantities = "label"
        conditions = ["number != 0.100445"]
        expected = [["label2"], ["label3"], ["label4"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["right", "string"]
        conditions = ["number != -9.0e-1", "number != 35"]
        expected = [[[1,2,3,4,5],"Adki bla hh"], [[0.2,0.3,0.4,100,1e4],"ACBMD QFY"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["label", "right"]
        conditions = ["left != 3"]
        expected = [["label1",[1,2,4,5]], ["label2",[13,24,47,58]], 
                    ["label3",[3,4,7,8]], ["label4",[0.2,0.3,100,1e4]]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["string"]
        conditions = ["number != 2.6"]
        expected = [["Adki bla hh"], ["AokE haaa"], ["Niak6^^ a"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["left"]
        conditions = ["right != 5"]
        expected = [[[1,2,3,4]], [[1,2,3,4,5]], [[1,2,4,5]], [[1,2,3,4,5]]]
        self.__compare_filter(quantities, conditions, expected)


    # Test filter #3
    # ==============
    def test_filter_3(self):
        '''Testing the >= operator. '''

        # Compare filtered data with the raw data
        quantities = "label"
        conditions = ["number >= 0.100445"]
        expected = [["label1"], ["label2"], ["label4"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["right", "string"]
        conditions = ["number >= 1.02"]
        expected = [[[13,24,35,47,58],"AokE haaa"], [[0.2,0.3,0.4,100,1e4],"ACBMD QFY"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["label", "right"]
        conditions = ["left >= 3"]
        expected = [["label1",[3,4,5]], ["label2",[35,47,58]], 
                    ["label3",[5,7,8]], ["label4",[0.4,100,1e4]]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["string"]
        conditions = ["number >= 2.6"]
        expected = [["AokE haaa"], ["ACBMD QFY"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["left"]
        conditions = ["right >= 5"]
        expected = [[[5]], [[1,2,3,4,5]], [[3,4,5]], [[4,5]]]
        self.__compare_filter(quantities, conditions, expected)


    # Test filter #4
    # ==============
    def test_filter_4(self):
        '''Testing the > operator. '''

        # Compare filtered data with the raw data
        quantities = "label"
        conditions = ["number > 0.100445"]
        expected = [["label2"], ["label4"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["right", "string"]
        conditions = ["number > 1.02"]
        expected = [[[13,24,35,47,58],"AokE haaa"], [[0.2,0.3,0.4,100,1e4],"ACBMD QFY"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["label", "right"]
        conditions = ["left > 3"]
        expected = [["label1",[4,5]], ["label2",[47,58]], 
                    ["label3",[7,8]], ["label4",[100,1e4]]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["string"]
        conditions = ["number > 2.6"]
        expected = [["AokE haaa"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["left"]
        conditions = ["right > 5"]
        expected = [[[1,2,3,4,5]], [[4,5]], [[4,5]]]
        self.__compare_filter(quantities, conditions, expected)


    # Test filter #5
    # ==============
    def test_filter_5(self):
        '''Testing the <= operator. '''

        # Compare filtered data with the raw data
        quantities = "label"
        conditions = ["number <= 0.100445"]
        expected = [["label1"], ["label3"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["right", "string"]
        conditions = ["number <= 1.02"]
        expected = [[[1,2,3,4,5],"Adki bla hh"], [[3,4,5,7,8],"Niak6^^ a"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["label", "right"]
        conditions = ["left <= 3"]
        expected = [["label1",[1,2,3]], ["label2",[13,24,35]], 
                    ["label3",[3,4,5]], ["label4",[0.2,0.3,0.4]]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["string"]
        conditions = ["number <= 2.6"]
        expected = [["Adki bla hh"], ["Niak6^^ a"], ["ACBMD QFY"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["left"]
        conditions = ["right <= 5"]
        expected = [[[1,2,3,4,5]], [[1,2,3]], [[1,2,3]]]
        self.__compare_filter(quantities, conditions, expected)


    # Test filter #6
    # ==============
    def test_filter_6(self):
        '''Testing the < operator. '''

        # Compare filtered data with the raw data
        quantities = "label"
        conditions = ["number < 0.100445"]
        expected = [["label3"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["right", "string"]
        conditions = ["number < 1.02"]
        expected = [[[1,2,3,4,5],"Adki bla hh"], [[3,4,5,7,8],"Niak6^^ a"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["label", "right"]
        conditions = ["left < 3"]
        expected = [["label1",[1,2]], ["label2",[13,24]], 
                    ["label3",[3,4]], ["label4",[0.2,0.3]]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["string"]
        conditions = ["number < 2.6"]
        expected = [["Adki bla hh"], ["Niak6^^ a"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["left"]
        conditions = ["right < 5"]
        expected = [[[1,2,3,4]], [[1,2]], [[1,2,3]]]
        self.__compare_filter(quantities, conditions, expected)


    # Test filter #7
    # ==============
    def test_filter_7(self):
        '''Testing the in operator. '''

        # Compare filtered data with the raw data
        quantities = "label"
        conditions = ["k in string"]
        expected = [["label1"], ["label2"], ["label3"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["right", "string"]
        conditions = ["label2 in label"]
        expected = [[[13,24,35,47,58],"AokE haaa"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["number", "label"]
        conditions = ["A in string", "h in string"]
        expected = [[0.100445, "label1"], [35, "label2"]]
        self.__compare_filter(quantities, conditions, expected)


    # Test filter #8
    # ==============
    def test_filter_8(self):
        '''Testing the not in operator. '''

        # Compare filtered data with the raw data
        quantities = "label"
        conditions = ["k not in string"]
        expected = [["label4"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["right", "string"]
        conditions = ["label2 not in label"]
        expected = [[[1,2,3,4,5],"Adki bla hh"], [[3,4,5,7,8],"Niak6^^ a"],
                    [[0.2,0.3,0.4,100,10000], "ACBMD QFY"]]
        self.__compare_filter(quantities, conditions, expected)

        # Compare filtered data with the raw data
        quantities = ["number", "label"]
        conditions = ["A not in string", "h not in string"]
        expected = [[-0.9, "label3"]]
        self.__compare_filter(quantities, conditions, expected)


    # Compare filter
    # ==============
    def __compare_filter(self, quantities, conditions, expected):
        '''Get filtered quantities and compared with expected results. '''

        # Get filtered quantities
        test = self.d.get_quantities(quantities, conditions=conditions)

        # Convert NumPy arrays to lists (for one-to-one comparison)
        test = self.__to_list(test)

        # Compare filter with expected results
        assert test == expected


    # To list converter
    # =================
    def __to_list(self, arr):
        '''Make sure all arrays are lists, not nd.array. '''

        # For each entry ..
        for i_entry in range(len(arr)):

            # For each quantity ..
            for i_quan in range(len(arr[i_entry])):

                # Convert to list if needed
                if isinstance(arr[i_entry][i_quan], np.ndarray):
                    arr[i_entry][i_quan] = list(arr[i_entry][i_quan])

        # Return the converted array
        return arr
