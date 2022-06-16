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


    # Test file #1
    # ============
    def test_file_1(self):

        # Read data file
        d = self.rdf.read_file("file_1.txt", "file_1_structure.txt")

        # Compare read data against raw data
        assert d.data["element"][0] == "H"
        assert d.data["element"][1] == "He"
        assert d.data["element"][2] == "Li"
        assert d.data["Z"][0] == 1
        assert d.data["Z"][1] == 2
        assert d.data["Z"][2] == 3
        assert d.data["value"][0] == 0.001
        assert d.data["value"][1] == 0.002
        assert d.data["value"][2] == 0.003

        # Test the number of entries
        assert d.nb_entries == 3
        assert d.nb_quantities == 3


    # Test file #2
    # ============
    def test_file_2(self):

        # Read data file
        d = self.rdf.read_file("file_2.txt", "file_2_structure.txt")

        # Compare read data against raw data
        assert d.data["label"][0] == "phrase #1"
        assert d.data["label"][1] == "phrase #2"
        assert d.data["value1"][0] == 1.42
        assert d.data["value1"][1] == -1e39
        assert d.data["value2"][0] == "aa"
        assert d.data["value2"][1] == "bb"

        # Test the number of entries and quantities
        assert d.nb_entries == 2
        assert d.nb_quantities == 3


    # Test file #3
    # ============
    def test_file_3(self):

        # Read data file
        d = self.rdf.read_file("file_3.txt", "file_3_structure.txt")

        # Compare read data against raw data
        assert d.data["comp1"][0] == "n"
        assert d.data["comp2"][0] == "p"
        assert d.data["comp3"][0] == ""
        assert d.data["comp4"][0] == ""
        assert d.data["comp5"][0] == ""
        assert d.data["comp1"][1] == "mt322"
        assert d.data["comp2"][1] == "n"
        assert d.data["comp3"][1] == "n"
        assert d.data["comp4"][1] == "n"
        assert d.data["comp5"][1] == "ds319"
        assert d.data["comp1"][2] == "he3"
        assert d.data["comp2"][2] == "t"
        assert d.data["comp3"][2] == ""
        assert d.data["comp4"][2] == ""
        assert d.data["comp5"][2] == ""
        assert d.data["comment"][0] == "wc12w"
        assert d.data["comment"][1] == "mo03w"
        assert d.data["comment"][2] == "ecw"
        assert d.data["q_value"][0] == 7.82300e-01
        assert d.data["q_value"][1] == 0.0
        assert d.data["q_value"][2] == -1.90000e-02
        assert d.data["a0"][0] == -6.781610e+00
        assert d.data["a1"][0] == 0
        assert d.data["a2"][0] == 0
        assert d.data["a3"][0] == 0
        assert d.data["a4"][0] == 0
        assert d.data["a5"][0] == 0
        assert d.data["a6"][0] == 0
        assert d.data["a0"][1] == -3.997350e+00
        assert d.data["a1"][1] == 0
        assert d.data["a2"][1] == 0
        assert d.data["a3"][1] == 0
        assert d.data["a4"][1] == 0
        assert d.data["a5"][1] == 0
        assert d.data["a6"][1] == 0
        assert d.data["a0"][2] == -3.246200e+01
        assert d.data["a1"][2] == -2.133800e-01
        assert d.data["a2"][2] == -8.215810e-01
        assert d.data["a3"][2] == 1.112410e+01
        assert d.data["a4"][2] == -5.773380e-01
        assert d.data["a5"][2] == 2.904710e-02
        assert d.data["a6"][2] == -2.627050e-01

        # Test the number of entries and quantities
        assert d.nb_entries == 3
        assert d.nb_quantities == 16


