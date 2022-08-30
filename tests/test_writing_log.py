# Tests for the writing process with logs
# Created by: Benoit Cote (August, 2022)

# Import Python packages
import numpy as np

# Import Interface tools
from Interface import read_data_file
from Interface import write_data_file

# TestWriting class
# =================
class TestWriting:
    """Class that tests the writing functionalities. """

    # Set path to the test files 
    root_path = "./tests/data/"

    # Instantiate the reading and writing scripts
    rdf = read_data_file.read_data_file(root_path=root_path)
    wdf = write_data_file.write_data_file(root_path=root_path)

    # Name of the file that will be used to write data
    out_name = "temp.txt"

    # Set the number of decimal points for writing files
    md = 5


    # Test file #1
    # ============
    def test_file_1(self):
        self.translate_compare("file_1.txt", "file_1_structure.txt", False)


    # Test file #4
    # ============
    def test_file_4(self):
        self.translate_compare("file_4.txt", "file_4_structure.txt", False)


    # Test file #5
    # ============
    def test_file_5(self):
        self.translate_compare("file_5.txt", "file_5_structure.txt", True)


    # Test file #7
    # ============
    def test_file_7(self):
        self.translate_compare("file_7.txt", "file_7_structure.txt", False)


    # Translate compare
    # =================
    def translate_compare(self, f, s, float_sci):

        # Read original data file from ascii to Data Interface
        d = self.rdf.read_file(f, s)

        # Write in log, read back, and compare with un-logged
        self.write_compare(s.replace(".txt","_log.txt"), d, float_sci)


    # Write compare
    # =============
    def write_compare(self, s, d, float_sci):

        # Write data file from Data Interface to ascii
        self.wdf.write_file(self.out_name, s, d, append=False, \
                max_decimal=self.md, float_sci=float_sci)

        # Read newly generated ascii file back to Data Interface
        d_new = self.rdf.read_file(self.out_name, s)

        # Compare the Interface Data objects
        self.compare_data(d, d_new)


    # Compare data
    # ============
    def compare_data(self, d, d_new):

        # Compare the number of entries and quantities
        assert d.nb_entries == d_new.nb_entries

        # Compare each quantity one by one
        for i_entry in range(d.nb_entries):
            for key in d.data:
                self.compare_quantity(d.data[key][i_entry], d_new.data[key][i_entry])


    # Compare quantity
    # ================
    def compare_quantity(self, q1, q2):

        # Compare the quantity type
        assert type(q1) == type(q2)

        # Compare one by one if lists
        if isinstance(q1, (list, np.ndarray)):
            for qq1, qq2 in zip(q1, q2):
                if isinstance(qq1, (int, float)):
                    assert '{:.4e}'.format(qq1) == '{:.4e}'.format(qq2)
                else:
                    assert qq1 == qq2

        # Compare directly if not lists
        else:
            if isinstance(q1, (int, float)):
                assert '{:.4e}'.format(q1) == '{:.4e}'.format(q2)
            else:
                assert q1 == q2
