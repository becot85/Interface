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

    # Precision digit when comparing data
    prec = 5


    # Test file #1
    # ============
    def test_file_1(self):

        # Read data file
        d = self.rdf.read_file("file_1.txt", \
                "file_1_structure.txt", test_path="file_1_test.txt")

        # Test the number of entries
        assert d.nb_entries == 3
        assert d.nb_quantities == 3

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

        # Read and test log data file
        d = self.rdf.read_file("file_1_log.txt", "file_1_structure_log.txt")
        assert d.nb_entries == 3
        assert d.nb_quantities == 4
        assert round(d.data["value"][0],self.prec) == 0.001
        assert round(d.data["value"][1],self.prec) == 0.002
        assert round(d.data["value"][2],self.prec) == 0.003
        assert d.data["log_value"][0] == -3.0
        assert d.data["log_value"][1] == -2.6989700043360187
        assert d.data["log_value"][2] == -2.5228787452803374



    # Test file #2
    # ============
    def test_file_2(self):

        # Read data file
        d = self.rdf.read_file("file_2.txt", \
                "file_2_structure.txt", test_path="file_2_test.txt")

        # Test the number of entries and quantities
        assert d.nb_entries == 2
        assert d.nb_quantities == 3

        # Compare read data against raw data
        assert d.data["label"][0] == "phrase #1"
        assert d.data["label"][1] == "phrase #2"
        assert d.data["value1"][0] == 1.42
        assert d.data["value1"][1] == -1e39
        assert d.data["value2"][0] == "aa"
        assert d.data["value2"][1] == "bb"

    # Test file #3
    # ============
    def test_file_3(self):

        # Read data file
        d = self.rdf.read_file("file_3.txt", \
                "file_3_structure.txt", test_path="file_3_test.txt")

        # Test the number of entries and quantities
        assert d.nb_entries == 3
        assert d.nb_quantities == 16

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


    # Test file #4
    # ============
    def test_file_4(self):

        # Read data file
        d = self.rdf.read_file("file_4.txt", 
                "file_4_structure.txt", test_path="file_4_test.txt")

        # Test the number of entries and quantities
        assert d.nb_entries == 2
        assert d.nb_quantities == 5

        # Compare read data against raw data
        assert d.data["id"][0] == 11
        assert d.data["id"][1] == 22
        assert d.data["label1"][0] == "multicolumn"
        assert d.data["label1"][1] == "Multicolumn"
        assert d.data["label2"][0] == 1.1
        assert d.data["label2"][1] == 2.2
        assert list(d.data["list"][0]) == ["a", "b", "c", "d"]
        assert list(d.data["list"][1]) == ["e", "f", "g", "h"]
        assert d.data["label3"][0] == "ok1"
        assert d.data["label3"][1] == "ok2"

        # Read and test log data file
        d = self.rdf.read_file("file_4_log.txt", "file_4_structure_log.txt")
        assert d.nb_entries == 2
        assert d.nb_quantities == 7
        assert round(d.data["id"][0],self.prec) == 11
        assert round(d.data["id"][1],self.prec) == 22
        assert round(d.data["label2"][0],self.prec) == 1.1
        assert round(d.data["label2"][1],self.prec) == 2.2
        assert d.data["log_id"][0] == 1.0413926851582251
        assert d.data["log_id"][1] == 1.3424226808222062
        assert d.data["log_label2"][0] == 0.04139268515822508
        assert d.data["log_label2"][1] == 0.3424226808222063


    # Test file #5
    # ============
    def test_file_5(self):

        # Read data file
        d = self.rdf.read_file("file_5.txt", \
                "file_5_structure.txt", test_path="file_5_test.txt")

        # Test the number of entries and quantities
        assert d.nb_entries == 2
        assert d.nb_quantities == 7

        # Compare read data against raw data
        assert d.data["comp1"][0] == "p"
        assert d.data["comp2"][0] == "gd134"
        assert d.data["comp3"][0] == "tb135"
        assert d.data["comp1"][1] == "t"
        assert d.data["comp2"][1] == "he3"
        assert d.data["comp3"][1] == ""
        assert d.data["comment"][0] == "aaaa"
        assert d.data["comment"][1] == "bbbbb"
        assert d.data["q_value"][0] == -1.18800E+00
        assert d.data["q_value"][1] == 1.85910e-02
        assert list(d.data["T9"][0]) == [1e-3, 2e-3, 3e-3]
        assert list(d.data["T9"][1]) == [1.1e-3, 2.2e-3, 3.3e-3]
        assert list(d.data["rate"][0]) == [0, 0, 1]
        assert list(d.data["rate"][1]) == [0.123E-09, 3.783E-09, 1.543E-09]

        # Read and test log data file
        d = self.rdf.read_file("file_5_log.txt", "file_5_structure_log.txt")
        assert d.nb_entries == 2
        assert d.nb_quantities == 8
        assert list(d.data["rate"][1]) == [0.123E-09, 3.783E-09, 1.543E-09]
        assert round(d.data["T9"][0][0],self.prec) == 1e-3
        assert round(d.data["T9"][0][1],self.prec) == 2e-3
        assert round(d.data["T9"][0][2],self.prec) == 3e-3
        assert round(d.data["T9"][1][0],self.prec) == 1.1e-3
        assert round(d.data["T9"][1][1],self.prec) == 2.2e-3
        assert round(d.data["T9"][1][2],self.prec) == 3.3e-3
        assert list(d.data["log_T9"][0]) == [-3.0, -2.69897000, -2.52287875]
        assert list(d.data["log_T9"][1]) == [-2.95860731, -2.65757732, -2.48148606]


    # Test file #6
    # ============
    def test_file_6(self):

        # Read data file
        d = self.rdf.read_file("file_6.txt", \
                "file_6_structure.txt", test_path="file_6_test.txt")

        # Test the number of entries and quantities
        assert d.nb_entries == 3
        assert d.nb_quantities == 3

        # Compare read data against raw data
        assert d.data["label"][0] == "the line #1"
        assert d.data["label"][1] == "the line #2"
        assert d.data["label"][2] == "the line #3"
        assert list(d.data["value1"][0]) == ["a", "b", "c", "d"]
        assert list(d.data["value1"][1]) == ["e", "f"]
        assert list(d.data["value1"][2]) == ["g"]
        assert list(d.data["value2"][0]) == ["aa", "bb", "cc", "dd"]
        assert list(d.data["value2"][1]) == ["ee", "ff"]
        assert list(d.data["value2"][2]) == ["gg"]


    # Test file #7
    # ============
    def test_file_7(self):

        # Read data file
        d = self.rdf.read_file("file_7.txt", \
                "file_7_structure.txt", test_path="file_7_test.txt")

        # Test the number of entries and quantities
        assert d.nb_entries == 4
        assert d.nb_quantities == 7

        # Compare read data against raw data
        assert list(d.data["common"][0]) == [1.1, 2.2, 3.3, 4.4, -1e10]
        assert list(d.data["common"][1]) == [1.1, 2.2, 3.3, 4.4, -1e10]
        assert list(d.data["common"][2]) == [1.1, 2.2, 3.3, 4.4, -1e10]
        assert list(d.data["common"][3]) == [1.1, 2.2, 3.3, 4.4, -1e10]
        assert list(d.data["a"][0]) == [6, 6]
        assert list(d.data["a"][1]) == [7, 7]
        assert list(d.data["a"][2]) == [8, 8]
        assert list(d.data["a"][3]) == [52, 52]
        assert list(d.data["z"][0]) == [3, 3]
        assert list(d.data["z"][1]) == [4, 4]
        assert list(d.data["z"][2]) == [3, 3]
        assert list(d.data["z"][3]) == [26, 26]
        assert list(d.data["T9"][0]) == [0.01, 0.011]
        assert list(d.data["T9"][1]) == [0.2, 0.202]
        assert list(d.data["T9"][2]) == [0.1, 0.103]
        assert list(d.data["T9"][3]) == [1.5, 1.504]
        assert list(d.data["rho"][0]) == [1, 2]
        assert list(d.data["rho"][1]) == [5, 6]
        assert list(d.data["rho"][2]) == [4, 5]
        assert list(d.data["rho"][3]) == [3, 4]
        assert list(d.data["r1"][0]) == [None, 1.1]
        assert list(d.data["r1"][1]) == [None, None]
        assert list(d.data["r1"][2]) == [2.2, None]
        assert list(d.data["r1"][3]) == [4.847, 4.233]
        assert list(d.data["r2"][0]) == [-100.000, -100.000]
        assert list(d.data["r2"][1]) == [-59.098, -54.914]
        assert list(d.data["r2"][2]) == [-100.000, -100.000]
        assert list(d.data["r2"][3]) == [-5.494, -5.353]


        # Read and test log data file
        d = self.rdf.read_file("file_7_log.txt", "file_7_structure_log.txt")
        assert d.nb_entries == 4
        assert d.nb_quantities == 9
        assert list(d.data["common"][0]) == [1.1, 2.2, 3.3, 4.4, -1e10]
        assert list(d.data["z"][3]) == [26, 26]
        assert list(d.data["T9"][0]) == [0.01, 0.011]
        assert list(d.data["log_rho"][0]) == [1, 2]
        assert list(d.data["log_rho"][1]) == [5, 6]
        assert list(d.data["log_rho"][2]) == [4, 5]
        assert list(d.data["log_rho"][3]) == [3, 4]
        assert round(d.data["rho"][0][0],self.prec) == round(10**(1),self.prec)
        assert round(d.data["rho"][0][1],self.prec) == round(10**(2),self.prec)
        assert round(d.data["rho"][1][0],self.prec) == round(10**(5),self.prec)
        assert round(d.data["rho"][1][1],self.prec) == round(10**(6),self.prec)
        assert round(d.data["rho"][2][0],self.prec) == round(10**(4),self.prec)
        assert round(d.data["rho"][2][1],self.prec) == round(10**(5),self.prec)
        assert round(d.data["rho"][3][0],self.prec) == round(10**(3),self.prec)
        assert round(d.data["rho"][3][1],self.prec) == round(10**(4),self.prec)
        assert list(d.data["log_r1"][0]) == [None, 1.1]
        assert list(d.data["log_r1"][1]) == [None, None]
        assert list(d.data["log_r1"][2]) == [2.2, None]
        assert list(d.data["log_r1"][3]) == [4.847, 4.233]
        assert d.data["r1"][0][0] == None
        assert round(d.data["r1"][0][1],self.prec) == round(10**(1.1),self.prec)
        assert d.data["r1"][1][0] == None
        assert d.data["r1"][1][1] == None
        assert round(d.data["r1"][2][0],self.prec) == round(10**(2.2),self.prec)
        assert d.data["r1"][2][1] == None
        assert round(d.data["r1"][3][0],self.prec) == round(10**(4.847),self.prec)
        assert round(d.data["r1"][3][1],self.prec) == round(10**(4.233),self.prec)


