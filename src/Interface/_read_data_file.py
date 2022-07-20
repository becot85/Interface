'''

    Creation date: October 5th, 2021
    Contributors: Benoit Cote (cotebenoit8@gmail.com)

'''

# Standard Python modules
import copy
import numpy as np

# Data object to collect the data dictionary resulting from reading
from . import data as dd
from . import data_file

# Interface toolkit
from . import interface_utils as utils


#######################
#  Declare the class  #
#######################
class read_data_file( data_file.data_file ):

    '''

    This class provides a general set of functions to read and store 
    data from a single file. Stored data are put in a data.py object.

    '''

    #################################
    #  Initialization of the class  #
    #################################
    def __init__(self, **kwargs):

        '''

        Initialize the read_data_file class.

        Arguments
        =========
            root_path (str): root path from which data files will be read

        '''

        # Initialize the data file class
        data_file.data_file.__init__(self, **kwargs)


    ###############
    #  Read file  #
    ###############
    def read_file(self, file_path, structure_path, test_path="", ignore_lines=[]):

        '''

        Extract quantities from all lines in the input file, and
        store them into a list of dictionaries, where each index 
        is one specific file entry.

        Arguments
        =========
            file_path (str): path to the input data file
            structure_path (str): path to the structure file (how to read data file)
            test_path (str): path to the test file to make sure reading was ok
            ignore_lines (list of int): line indexes to be ignored

        '''

        # Initialize reading process
        i_line, line = self.__init_reading(file_path, structure_path, ignore_lines)

        # Declare list of entries and structures that have been applied
        entries = []
        read_structure = []

        # While the file is not read completely ..
        ongoing = True
        while ongoing:

            # Initialize the quantities of the upcoming entry
            entries.append([])

            # For each sub-bloc within the main bloc ..
            for sub_bloc in self.__bloc:

                # Find the number of time this sub-bloc should be
                # repeated to gather the quantities of a file entry
                nb_repeats = self.__get_nb_repeats(sub_bloc, entries[-1])
                for i_r in range(nb_repeats):

                    # For each line of the sub-bloc ..
                    for structure in sub_bloc["lines"]:

                        # Pre-screen the structure content to gain insights on how to proceed
                        skip, structure, read_structure, multiline, ml_is_digit, ml_end_point = \
                                self.__screen_structure(structure, read_structure)

                        # If there is something to collect on this line ..
                        if not skip:
                            if not structure == None:

                                # If the quantities cover several lines ..
                                if multiline:

                                    # Collect all the quantities listed on these lines
                                    i_line, line, entries = self.__extract_ml_quantities(\
                                        i_line, line, structure, entries, ml_is_digit, ml_end_point)

                                # If the quantities are not listed over several lines ..
                                else:

                                    # Add the quantity directly to the dictionary
                                    entries[-1].append(self.__get_quantities(\
                                            line, structure, split_character=None))

                            # Update the targetted line
                            i_line, line = self.__update_line(i_line)
                            if i_line == self.__nb_lines:
                                ongoing = False
                                break

        # Delete temporary variables that aimed to assist this read_file function
        self.__delete_temp_variables()

        # Generate and return the Data Interface object (if everything went well)
        return self.__generate_DI(entries, test_path)


    ##################
    #  Init reading  #
    ##################
    def __init_reading(self, file_path, structure_path, ignore_lines):

        '''

        Declare and initialize variables for the reading process.

        Arguments
        =========
            file_path (str): path to the input data file
            structure_path (str): path to the structure file (how to read data file)
            test_path (str): path to the test file to make sure reading was ok
            ignore_lines (list of int): line indexes to be ignored

        '''

        # Read the instructions on how to read the data file
        bloc, header, header_keys = self._create_bloc_structure(structure_path)

        # Read all the lines of the input file
        lines, nb_lines = self._read_lines(file_path)

        # Temporarily assign self to recurent variables
        self.__bloc = bloc
        self.__header = header
        self.__header_keys = header_keys
        self.__ignore_lines = ignore_lines
        self.__lines = lines
        self.__nb_lines = nb_lines

        # Initialize the line index
        i_line, line = self.__get_start_line_index()

        # Return dynamic variables
        return i_line, line


    ###########################
    #  Delete temp variables  #
    ###########################
    def __delete_temp_variables(self):

        '''

        Delete self.__ variables that were temporarily defined to assist
        the reading process within the read_file function.

        '''

        # Delete variables
        del self.__bloc
        del self.__header
        del self.__header_keys
        del self.__ignore_lines
        del self.__lines
        del self.__nb_lines


    ######################
    #  Screen structure  #
    ######################
    def __screen_structure(self, structure, read_structure):

        '''

        Pre-screen the structure to gain insights on how to proceed
        with the upcoming data extraction process.

        Arguments
        =========
            structure (dict): one line of a structure sub-bloc
            read_structure (list): list of already-covered structures

        '''

        # Check whether the upcoming reading should be skipped
        skip, read_structure = self.__check_skip(structure, read_structure)

        # If upcoming data is spread over multiple lines ..
        if "$MULTILINE" in structure:

            # Set multiline flag
            multiline = True

            # Set multiline variables if number of loops is provided 
            if utils.remove_all_spaces(structure["$MULTILINE"]).isdigit():
                ml_is_digit = True
                ml_end_point = int(structure["$MULTILINE"])

            # Set multiline variables if number of loops is dynamic 
            else:
                ml_is_digit = False
                ml_end_point = utils.remove_initial_spaces(structure["$MULTILINE"])

        # Set multiline flag to False if upcoming data is on one line
        else:
            multiline = False
            ml_is_digit = None
            ml_end_point = None

        # Remove header flags from structure dictionary
        structure = self._remove_flags(structure)

        # Return pre-screen result
        return skip, structure, read_structure, multiline, ml_is_digit, ml_end_point


    ################
    #  Check skip  #
    ################
    def __check_skip(self, structure, read_structure):

        '''

        Keep track of the structures already covered and look
        for the $ONCE header to make sure it is only convered
        once throughout the reading.

        Arguments
        =========
            structure (dict): one line of a structure sub-bloc
            read_structure (list): list of already-covered structures


        '''

        # First assume that the upcoming structure should not be skipped
        skip = False

        # If this is not the first time the structure is applied
        if structure in read_structure:

            # Skip if the bloc should be only read once
            if "$ONCE" in list(structure.keys())[0]:
                skip = True

        # If this is the first time the structure is applied ..
        else:

            # Add it to the list of treated structures
            read_structure.append(structure)

        # Return check result
        return skip, read_structure


    ###########################
    #  Extract ML quantities  #
    ###########################
    def __extract_ml_quantities(self, i_line, line, structure, entries,\
                                      ml_is_digit, ml_end_point):

        '''

        Extract all quantities involved in a $MULTILINE command and 
        add them to the entries array.

        Arguments
        =========
            i_line (int): current line index
            line (str): current line
            structure (dictionary): instructions on to extract quantities
            entries: combined dictionaries (the content of the input file)
            ml_is_digit (bool): True if the number of loops is provided
            ml_end_point (str or int): Endpoint flag or number of loops 

        '''

        # Create an entry for the data dictionary
        entries[-1].append(dict())

        # If the number of multiline loops is provided ..
        if ml_is_digit:

            # Collect quantities over a fixed number of loops
            for i_loop in range(ml_end_point):

                # Collect the quantities on the line
                entries = self.__extract_ml_line(line, structure, entries)

                # Go to the next line if needed
                if not i_loop == (ml_end_point - 1):
                    i_line, line = self.__update_line(i_line)

        # If the multiline loop is dynamic ..
        else:

            # Collect quantities until the end point is found ..
            while not ml_end_point in line:

                # Collect the quantities on the line
                entries = self.__extract_ml_line(line, structure, entries)

                # Go to the next line
                if i_line == (self.__nb_lines - 1):
                    break
                else:
                    i_line, line = self.__update_line(i_line, stop=ml_end_point)

        # Return updated variables
        return i_line, line, entries


    #####################
    #  Extract ML line  #
    #####################
    def __extract_ml_line(self, line, structure, entries):

        '''

        Extract quantities from a line and add them to the entries
        array knowing that we are in the $MULTILINE mode and that
        each item in the listare progressively being appended.

        Arguments
        =========
            line (str): current line
            structure (dictionary): instructions on to extract quantities
            entries: combined dictionaries (the content of the input file)

        '''

        # Collect the quantities on the line
        quantities = self.__get_quantities(line, structure)

        # For each quantity ..
        for quantity in quantities:

            # Add the quantity to the array
            if not quantity in entries[-1][-1].keys():
                entries[-1][-1][quantity] = []
            entries[-1][-1][quantity].append(quantities[quantity])

        # Return the updated entries array
        return entries


    #################
    #  Update line  #
    #################
    def __update_line(self, i_line, stop=None):

        '''

        Increment the line index within the data extraction process,
        taking into account lines that should be ignored. This also
        returns the targetted line (or None if outside range).

        Arguments
        =========
            i_line (int): current line index
            stop (string): Series of character found in a line that stops the update process

        '''

        # Increment the line index
        i_line += 1
        if i_line >= self.__nb_lines:
            return self.__nb_lines, None

        # Increment the line until this is a line to be treated
        while i_line in self.__ignore_lines or self.__should_ignore(self.__lines[i_line]):

            # Stop if the line includes a flag that tell a multiline process to stop
            if not stop == None:
                if stop in self.__lines[i_line]:
                    break

            # Go to the next line
            i_line += 1

            # Return if the index is going out of range
            if i_line == self.__nb_lines:
                return i_line, None
        
        # Return the new line index
        return i_line, self.__lines[i_line]


    ##########################
    #  Get start line index  #
    ##########################
    def __get_start_line_index(self):

        '''

        Find the line index where the reading process should start within the 
        input data file.

        '''

        # If there is a specific starting flag included in the structure header ..
        if "START" in self.__header_keys:

            # While the current line does include the flag ..
            i_line = 0
            while not self.__header["START"] in self.__lines[i_line]:

                # Skip the line
                i_line += 1

                # Send an error if the starting point is not found
                if i_line == self.__nb_lines:
                    print("Error - START flag "+self.__header["START"]+" not found within the file.")
                    return None

        # If no starting flag is used ..
        else:

            # Get the first line index that is not ignored
            i_line, line = self.__update_line(-1)

        # Return the starting line index
        return i_line, self.__lines[i_line]


    ###################
    #  Should ignore  #
    ###################
    def __should_ignore(self, line):

        '''

        Define whether a given line in the input file should be 
        ignored, based on the header provided with the structure file.

        Arguments
        =========
            line (str): current line

        '''

        # Return False if there is no "IGNORE" in the header
        if not "IGNORE" in self.__header_keys:
            return False

        # For each set of characters that flags a line as a line to be ignored ..
        for ign in self.__header["IGNORE"]:

            # Return True if these character are found in the line
            if ign in line:
                return True

        # Return False if the line should not be ignored
        return False


    ####################
    #  Get nb repeats  #
    ####################
    def __get_nb_repeats(self, sub_bloc, entry):

        '''

        Find the number of time a given sub_block should be repeated
        in order to gather the quantities of a file entry.

        Arguments
        =========
            sub_bloc: bloc structure within the main bloc
            entry: quantities found within the sub_bloc

        '''

        # Repeat once if no specification was given
        if not "repeat" in sub_bloc.keys():
            return 1

        # Copy the repeating instruction
        rp = sub_bloc["repeat"]

        # Return the number of repeats if directly provided
        if isinstance(rp, int):
            return rp

        # If a variable is given ..
        if isinstance(rp, str):

            # Find the variable setting the number of repeats
            for dct in entry:
                if rp in dct.keys():
                    return dct[rp]

            # Print an error if the variable is not found
            print("Error - "+rp+" variable not found in __get_nb_repeats().")


    ####################
    #  Get quantities  #
    ####################
    def __get_quantities(self, line, structure, split_character=None):

        '''

        Take a line (single string), extract the quantities following
        a given split structure, and return the quantities in a dictionary.

        Arguments
        =========
            line (string): all characters of a given line from the input file
            structure (dictionary): instructions on to extract quantities
            split_character (string): special character used to split the line
                                      None: split without character


        '''

        # Declare the quantities that will be extracted from the line
        quantities = dict()

        # Split the line (if needed)
        ls = self.__split_line(line, structure, split_character)

        # Assing a list to the quantity is a simple split is used
        if len(structure) == 1 and type(ls) == list and len(ls) > 1:
            for quantity in structure.keys():
                quantities[quantity] = ls
                try:
                    for i_item in range(len(ls)):
                        quantities[quantity][i_item] = structure[quantity][0](ls[i_item])
                except:
                    quantities[quantity] = None

        # If there is only one quantity in the split line ..
        elif type(ls) == str:

            # Adjust the single variable type
            for quantity in structure.keys():
                try:
                    quantities[quantity] = structure[quantity](ls)
                except:
                    quantities[quantity] = None

        # If each value in ls has its own quantity label ..
        else:

            # Adjust the variable type of each quantity
            for value, quantity in zip(ls, structure.keys()):
                try:
                    quantities[quantity] = structure[quantity][0](value)
                except:
                    quantities[quantity] = None

        # Return empty dictionary if all quantities are None
        if len(quantities) == list(quantities.values()).count(None):
            return dict()

        # Return the quantities extracted from the line
        return quantities


    ################
    #  Split line  #
    ################
    def __split_line(self, line, structure, split_character):

        '''

        Split a line following a given instruction.

        Arguments
        =========
            line (string): all characters of a given line from the input file
            structure (dictionary): instructions on to extract quantities
            split_character (string): special character used to split the line
                                      None: split without character

        '''

        # Copy an example of the input structuree
        ex_st = structure[list(structure.keys())[0]]

        # Return the line if there is no split
        if not type(ex_st) == tuple:
            return line

        # If the .split() function is used with specific index ..
        if type(ex_st[1]) == int:

            # Define the split line
            first_split = line.split(split_character)
            ls = []

            # Extract manually each quantiry
            for q in structure:
                ls.append(first_split[structure[q][1]])

            # Return the quantities
            return ls

        # If the .split() function is used without specific index ..
        if ex_st[1] == "split":

            # Return the simple split
            return line.split(split_character)

        # If spaces are used to define where are the quantities ..
        if type(ex_st[1]) == tuple:

            # Define the split line
            ls = []
            
            # Exctact manually each quantity
            for q in structure:
                i_low = structure[q][1][0]
                i_upp = structure[q][1][1]
                ls.append(line[i_low:i_upp+1])

            # Return the quantities
            return ls


    ###################
    #  Clean strings  #
    ###################
    def __clean_strings(self, entries):

        '''

        Remove extra spaces from all strings in the entries dictionary.

        '''

        # For each entry ..
        for i_entry in range(len(entries)):

            # For each dictionary (each file line) in that entry ..
            for i_dct in range(len(entries[i_entry])):

                # For each quantity in that file line ..
                for quantity in entries[i_entry][i_dct].keys():

                    # Remove extra space if it is a string
                    if type(entries[i_entry][i_dct][quantity]) == str:
                        entries[i_entry][i_dct][quantity] = \
                            utils.remove_extra_spaces(\
                                entries[i_entry][i_dct][quantity])

        # Return the cleaned dictionaries
        return entries


    #################
    #  Generate DI  #
    #################
    def __generate_DI(self, entries, test_path):

        '''

        From a raw entries dictionary read from an ascii file, generate
        and return a Data Interface object validated  with a test file
        if provided.

        Arguments
        =========
            entries: combined dictionaries (the content of the input file)
            test_path (str): path to the test file to make sure reading was ok

        '''

        # Get rid of extra spaces
        entries = self.__clean_strings(entries)

        # Combine the dictionaries if each entry into one single dictionary
        entries, quantities, quantities_type = self.__clean_dictionaries(entries)

        # Create a data object
        data = self.__transpose_dictionary(entries, quantities, quantities_type)

        # Return the Interface Data object (if everything went well)
        if self.__reading_validated(data, test_path):
            return data
        else:
            return dd.data(dict())


    ########################
    #  Clean dictionaries  #
    ########################
    def __clean_dictionaries(self, entries):

        '''

        Take each entry of a read file, and combine all dictionaries
        (originating from different file lines within an entry) in
        order to only have one single dictionary per entry.

        Argument
        ========
            entries: combined dictionaries (the content of the input file)

        '''

        # Declare the list of all possible dictionary keys
        quantities = []
        quantities_type = dict()

        # For each entry of the file ..
        for i_entry in range(len(entries)):

            # Declare the key counter
            # How many times a dictionary key appears in the combined dictionary
            q_count = dict()

            # Declare the combined dictionary
            new_dct = dict()

            # For each dictionary (each line) within the entry ..
            for dct in entries[i_entry]:

                # For each quantity within that line ..
                for q in dct.keys():

                    # Check if the quantity exists in the combined dictionary
                    if q in q_count:
                        q_count[q] += 1
                    else:
                        q_count[q] = 1

                    # Enter the quantity in the combined dictionary
                    if q_count[q] == 1:
                        new_dct[q] = copy.deepcopy(dct[q])
                    else:
                        new_str = q+" "+str(q_count[q])
                        new_dct[new_str] = copy.deepcopy(dct[q])
                        quantities.append(new_str)
                        quantities_type[new_str] = type(dct[q])

                    # Add the key (quantity) in the list if needed
                    if not q in quantities:
                        quantities.append(q)
                        quantities_type[q] = type(dct[q])

            # Overwrite the entier entry
            entries[i_entry] = new_dct

        # Remove empty entries
        entries = list(filter(lambda x: x != dict(), entries))

        # Return the cleaned dictionary
        return entries, quantities, quantities_type


    ##########################
    #  Transpose dictionary  #
    ##########################
    def __transpose_dictionary(self, entries, quantities, quantities_type):

        '''

        Take the combined dictionaries (entries) and convert them
        in a way that each quantity has an array corresponding to the
        full list of entries.

        Arguments
        =========
            entries: combined dictionaries (the content of the input file)
            quantities: dictionary key (list of quantities in the input file)
            quantities_type: str, int, float, etc.

        '''

        # Declare the list of quantities
        data = dict()
        for q in quantities:
            data[q] = []

        # For each entry ..
        for i_entry in range(len(entries)):

            # Available quantities for this entry
            key_available = entries[i_entry].keys()

            # For each quantity ..
            for q in quantities:

                # Add the quantity value in the data dictionary
                if q in key_available:
                    if "$ONCE" in q:
                        data[q.split("$ONCE")[0]] = [entries[i_entry][q]] * len(entries)
                        del data[q]
                    else:
                        data[q].append(entries[i_entry][q])
                else:
                    if not "$ONCE" in q:
                        if quantities_type[q] == str:
                            data[q].append("")
                        else:
                            data[q].append(0)

        # Create a data instance
        return dd.data(data)


    #######################
    #  Reading validated  #
    #######################
    def __reading_validated(self, data, test_path):

        '''

        Compare some of the data read using Interface with the expected data
        from specific entries provided within the test file. The function 
        returns False if an inconclusive test was conducted. Returns True
        if the test was conclusive, or if no test could be performed.

        Arguments
        =========
            data (Data Interface object): data read from the input file
            test_path (str): path to the test file to make sure reading was ok

        '''

        # Make sure a test file is provided
        if isinstance(test_path, str):
            if test_path == "":
                return True
        else:
            print("Error - 'test_path' variable should be a string.")
            print("      - No test performed.")
            return True

        # Build the list of dictionaries containing expected quantities
        d_list = self.__build_test_case(test_path)
        if d_list == None:
            return True

        # For each tested entries ..
        for d in d_list:
            i_entry = d["i_entry"]

            # For each quantity in the test case ..
            for quantity, value in d.items():
                if not quantity == "i_entry":

                    # Copy (reformat if needed) read data
                    if isinstance(data.data[quantity][i_entry], np.ndarray):
                        read_value = list(data.data[quantity][i_entry])
                    else:
                        read_value = data.data[quantity][i_entry]

                    # Error message if the comparison failed ..
                    if not read_value == value:
                        print("Error - Test failed. Please revisit structure file.")
                        print("      - i_entry:", i_entry)
                        print("      - quantity:", quantity)
                        print("      - expected:", value)
                        print("      - read:", read_value)
                        return False

        # Print notice of success if all tests passed
        print("Reading test successful.")
        return True


    #####################
    #  Build test case  #
    #####################
    def __build_test_case(self, test_path):

        '''

        Read a reading test file and build a list of dictionaries representing
        the expected quantities of specific data entries.

        Argument
        ========
            test_path (str): path to the test file to make sure reading was ok

        '''

        # Declare the list of expected quantities (dictionaries)
        d_list = []

        # Read test file
        lines, nb_lines = self._read_lines(test_path)

        # Try to build the test case
        try:

            # For each line in the test file ..
            for line in lines:

                # If there is something in that line ..
                if not self._line_is_empty(line):

                    # Split line
                    quantity, value = self.__split_test_line(line)
                    if quantity == None:
                        return None

                    # Create new entry
                    if quantity == "i_entry":
                        d_list.append({"i_entry": int(value)})

                    # Collect expected quantities
                    d_list[-1][quantity] = value

        # Send warning if test case could not be built
        except:
            print("Error - Test file not formated correctly.")
            print("      - No test performed.")
            return None

        # Return the test case
        return d_list


    #####################
    #  Split test line  #
    #####################
    def __split_test_line(self, line):

        '''

        From a line taken from the test file, extract quantities and format 
        them according to the requested type.

        Argument
        ========
            line (str): line extracted from the test file

        '''

        # Extract quantity label
        split = line.split(":")
        quantity = split[0]
        split_value = split[1]

        # Return entry info if this is an entry index
        if quantity == "i_entry":
            return quantity, int(split_value)

        # Find the string index of the first instance of ","
        # Do not use split(",") since value can include ","
        if "," in split_value:
            i_split = 0
            while not split_value[i_split] == ",":
                i_split += 1

        # Print error if no comma were found
        else:
            print("Error - File test format issue.")
            print("      - No ',' found in the line '"+line+"'.")
            print("      - No test performed.")
            return None, None

        # Extract value type and value
        v_type = split_value[:i_split].replace(" ","")
        v_type = self._return_type(v_type)
        value = split_value[i_split+1:]
        value = utils.remove_initial_spaces(value)

        # If the expected value is a list ..
        if len(value) > 0:
            if value[0] == "[":

                # Return nothing if the list has no end ..
                value = value.replace(" ","")
                if not value[-1] == "]":
                    return None

                # Extract raw items from the list
                value_list_str = value[1:-1].split(",")

                # Create list of expected values
                value_list = []
                for v in value_list_str:
                    value_list.append(v_type(v))

                # Return the split test line
                return quantity, value_list

        # Return the expected value if not a list ..
        return quantity, v_type(utils.remove_extra_spaces(value))

            

