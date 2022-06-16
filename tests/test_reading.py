# Tests for the reading process
# Created by: Benoit Cote (June, 2022)

# Import Interface tools
from Interface import read_data_file

# TestReading class
# =================
class TestReading:
    """Class that tests the reading functionalities. """

    # Instantiate the reading scripts and setting root folder
    rdf = read_data_file.read_data_file(root_path="./tests/data/")

    # Compare values
    # ==============
    def compare_values(self, data, test_case):
        """Compare raw values with the ones read from a file. """

        # Test each case
        for i_entry, key, value in test_case:
            assert data[key][i_entry] == value


    # Test file #1
    # ============
    def test_file_1(self):

        # Read data file
        d = self.rdf.read_file("file_1.txt", "file_1_structure.txt")

        # Fill the raw values to be tested
        test_case = []
        test_case.append([0,"element","H"])
        test_case.append([1,"element","He"])
        test_case.append([2,"element","Li"])
        test_case.append([0,"Z",1])
        test_case.append([1,"Z",2])
        test_case.append([2,"Z",3])
        test_case.append([0,"value",0.001])
        test_case.append([1,"value",0.002])
        test_case.append([2,"value",0.003])

        # Compare raw values with the ones read from file
        self.compare_values(d.data, test_case)


