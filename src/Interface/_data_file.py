'''

    Creation date: February 1st, 2022
    Contributors: Benoit Cote (cotebenoit8@gmail.com)

'''

# Import Interface toolkit
from . import interface_utils as utils

# Declare the class
class data_file( object ):

    '''

    This class provides a general common functions and variables for
    reading data from files and writing data to files. This class is
    currently inherited by _read_data_file.py and _write_data_file.py.

    '''

    #################################
    #  Initialization of the class  #
    #################################
    def __init__(self, root_path=""):

        '''

        Initialize the data_file class.

        Arguments
        =========
            root_path (str): root path where data files can be read and written

        '''

        # Store the root path for future use
        if len(root_path) > 0:
            if not root_path[-1] == "/":
                root_path += "/"
        self._root_path = root_path

        # Define the header variables that are currently treated by the reading code
        self.__valid_headers = ["START", "IGNORE", "MULTILINE", "ONCE"]
        self.__not_main_headers = ["MULTILINE", "ONCE"]


    ###########################
    #  Create bloc structure  #
    ###########################
    def _create_bloc_structure(self, structure_path):

        '''

        Read the input structure of a file, and create the "bloc" structure
        that provides instructions to the code on how to read the data file.

        Argument
        ========
            structure_path (string): path to the input structure file

        '''

        # Collect the lines of the structure file
        lines = self._read_lines(structure_path)
        nb_lines = len(lines)

        # Read structure file header (identified with  the $ symbol)
        i_start, header = self.__read_header(lines, nb_lines)
        i_start = self.__skip_empty_lines(i_start, lines, nb_lines)

        # Define the bloc structure
        bloc = []
        bloc.append({"lines":[]})
        bloc[-1]["lines"].append(dict())
        post = ""

        # For each line in the structure file ..
        for i_line in range(i_start, len(lines)):
            line = lines[i_line]

            # Start a new bloc line if needed
            if self._line_is_empty(line) and not line == lines[-1]:
                bloc[-1]["lines"].append(dict())
                post = ""
            else:

                # Flag the bloc line if this will only be read once
                if "$ONCE" in line:
                    post = "$ONCE"
                else:

                    # Collect the quantity label
                    l_split = line.split(":")
                    quantity = l_split[0]+post

                    # Collect the header flag (if provided)
                    if quantity[0] == "$":
                        structure = utils.remove_initial_spaces(l_split[1])

                    # Collect the type and location of the quantity within the file
                    else:
                        structure = self.__format_structure(l_split[1])

                    # Include the reading instructions into the bloc structure
                    bloc[-1]["lines"][-1][quantity] = structure

        # Return the reading instructions
        return bloc, header


    #################
    #  Read header  #
    #################
    def __read_header(self, lines, nb_lines):

        '''

        Read file header and return a dictionary with general reading instructions

        Argument
        ========
            lines (list of str): lines read from an input file
            nb_lines (int): len(lines)

        '''

        # Declare the header dictionary
        header = dict()

        # Get rid of empty initial lines (if any)
        i_line = self.__skip_empty_lines(0, lines, nb_lines)

        # For each header line in the input file ..
        line = utils.remove_initial_spaces(lines[i_line])
        while line[0] == "$":

            # Split the line
            if ":" in line:
                l_split = line.split(":")
            else:
                l_split = [line,""]
            flag = l_split[0][1:]

            # Stop the header process if the flag is not a main-header flag
            if flag in self.__not_main_headers:
                break

            # Create a new header entry
            if flag == "IGNORE":
                if not flag in header.keys():
                    header[flag] = []
                header[flag].append(utils.remove_initial_spaces(l_split[1]))
            else:
                header[flag] = utils.remove_initial_spaces(l_split[1])

            # Print warning message if the header is treated by the code
            if not flag in self.__valid_headers:
                print("Warning - "+flag+" is not a valid header.")

            # Change line
            i_line += 1
            if self._line_is_empty(lines[i_line]):
                break
            line = utils.remove_initial_spaces(lines[i_line])

        # Return the header dictionary
        return i_line, header


    ################
    #  Read lines  #
    ################
    def _read_lines(self, file_path):

        '''

        Read and return all lines from the input file, without "\n"

        Arguments
        =========
            file_path (string): path to the input data file

        '''

        # Declare the list of lines
        lines = []

        # For each line in the input file ..
        with open(self._root_path+file_path) as f:
            for line in f:

                # Collect the line without the "\n" character
                if line[-1:] == "\n":
                    lines.append(line[:-1])
                else:
                    lines.append(line)

        # Close input file
        f.close()

        # Return the list of individual lines
        return lines


    ######################
    #  Skip empty lines  #
    ######################
    def __skip_empty_lines(self, i_line, lines, nb_lines):

        '''

        From a given line index, skip all lines that are empty, and
        return the new line index

        Arguments
        =========
            i_line (int): line index within lines
            lines (list of strings): list of lines read from an input file
            nb_lines (int): len(lines)

        '''

        # While the current line is empty ..
        while self._line_is_empty(lines[i_line]):

            # Go to the next line
            i_line += 1

            # Return None (warning sign) if this is beyond the last line
            if i_line == nb_lines:
                return None

        # Return the new non-empty line index
        return i_line


    ###################
    #  Line is empty  #
    ###################
    def _line_is_empty(self, line):

        '''

        Return True is the input line is either empty or only filled with spaces

        Argument
        ========
            line (str): input line of text

        '''

        # Return True is there is nothing
        if line == "":
            return True

        # Scan through all characters
        char = []
        for c in line:
            if not c in char:
                char.append(c)
                if len(char) > 1:
                    return False

        # Empty if only composed of " " and "\n"
        if char == [" "]:
            return True
        else:
            return False


    ######################
    #  Format structure  #
    ######################
    def __format_structure(self, structure):

        '''

        Convert structure (string) read from the input structure file into a
        format that goes into the "bloc" structure (reading instructions).

        Argument
        ========
            structure (string): structure of a quantity from the structure file

        '''

        # Split the string
        s_split = structure.split(",")

        # Get the type of the quantity
        q_type = self._return_type(s_split[0])

        # Return only the type if no location is given
        if len(s_split) == 1:
            return q_type

        # If the quantity has multiple locations (is an array)
        if "multicolumn" in s_split[1]:

            # Set the location to a string split, with undefined end
            q_location = "split"

        # If the location is given by a lower and upper index location ..
        elif "-" in s_split[1]:

            # Create a tuple for the location
            i_low = int(s_split[1].split("-")[0])
            i_upp = int(s_split[1].split("-")[1])
            q_location = (i_low,i_upp)

        # If the location is a simple split index
        else:
            
            # Copy the location
            q_location = int(s_split[1])

        # Return a tuple to specify the type and location of the quantity
        # including additional special instructions (e.g. multiline)
        if len(s_split) == 2:
            return (q_type, q_location)
        elif len(s_split) == 3:
            return (q_type, q_location, utils.remove_initial_spaces(s_split[2]))
        else:
            return None


    #################
    #  Return type  #
    #################
    def _return_type(self, str_type):

        '''

        Convert a string type (e.g. "float") into a Python type (e.g. float).

        Argument
        ========
            str_type (string): string type (e.g. "int")

        '''

        # Return int
        if utils.remove_extra_spaces(str_type) == "int":
            return int

        # Return string
        if utils.remove_extra_spaces(str_type) == "str":
            return str

        # Return float
        if utils.remove_extra_spaces(str_type) == "float":
            return float

