'''

    Creation date: February, 2022
    Contributors: Benoit Cote (cotebenoit8@gmail.com)

'''

# Standard Python modules
import sys
import numpy as np

# Data object to collect the data dictionary resulting from reading
from . import data as dd
from . import data_file

# Import Interface toolkit
from . import interface_utils as utils

# Declare the class
class write_data_file( data_file.data_file ):

    '''

    This class provides a general set of functions to write a data (ascii) 
    file from a data object, following an input structure file. 

    '''


    #################################
    #  Initialization of the class  #
    #################################
    def __init__(self, empty_char="&", spacing=" ", float_sci=False, **kwargs):

        '''

        Initialize the write_data_file class.

        Arguments
        =========
            empty_char (str): character that will be outputed when no data available
            spacing (str): characters that provide spacing in between quantities
            root_path (str): root path to which data files will be written
            float_sci (bool): if True, floats will be printed in scientific notations

        '''

        # Initialize the data file class
        data_file.data_file.__init__(self, **kwargs)

        # Assign self variables
        self.__spacing = spacing
        self.__empty_char = empty_char + self.__spacing
        self.__float_sci = float_sci


    ################
    #  Write file  #
    ################
    def write_file(self, file_path, structure_path, data, \
                   max_entry_per_w=100, max_decimal=3, \
                   append=False, float_sci=False):

        '''

        Write a data file out of a data object, following a given
        structure file.

        Arguments
        =========
            file_path (str): path to data file to be writen
            structure_path (str): path to the structure file (how to read data file)
            data (Data object): object containing the data to be writen
            max_decimal (int): number of decimals for digits in scientific notation
            append (bool): If True, writing process will add to an existing file

        '''

        # Overwrite scientific notation flag
        self.__float_sci = float_sci

        # Initialize writing process (returns output file)
        f, bloc = self.__init_writing(file_path, structure_path, data, max_decimal, append)

        # Declare output text and structures that have been applied
        text = ""
        read_structure = []

        # Copy data and declare number of accumulated entries
        d = data.data
        cumul = 0

        # For each entry in the data object ..
        for i_entry in range(data.nb_entries):

            # For each sub-bloc within the main structure bloc ..
            for sub_bloc in bloc:

                # For each structure line representing this entry ..
                for structure in sub_bloc["lines"]:

                    # Pre-screen the structure content to gain insights on how to proceed
                    skip, structure, read_structure, multiline, ml_is_digit, ml_end_point = \
                        self._screen_structure(structure, read_structure)

                    # If there is something to be written (i.e. ignore $ONCE) ..
                    if not skip:

                        # Reformat keys and positions for the writing process
                        keys, positions = self.__reformat_key_pos(structure)

                        # If quantities (lists) should be outputed on multiple lines ..
                        if multiline:

                            # Extract the number of lines needed
                            key_temp = list(structure.keys())[0]
                            nb_lines = len(d[key_temp][i_entry])

                            # Collect quantities for each line (each array index) ..
                            for i_list in range(nb_lines):
                                text += self.__generate_line(i_entry, keys, positions, d, \
                                        max_decimal, i_list=i_list)

                            # Add multiline endpoint if needed
                            if not ml_is_digit:
                                text += ml_end_point + "\n"

                        # Collect quantities directly if positioned on a single line ..
                        else:
                            text += self.__generate_line(i_entry, keys, positions, d, max_decimal)

            # Write if needed, and clear the memory
            # Should be last operation of the 'for i_entry' loop
            cumul += 1
            if cumul == max_entry_per_w:
                f.write(text)
                text = ''
                cumul = 0

        # Write the remaining part
        if not text == '':
            f.write(text)

        # Close the file
        f.close()


    ##################
    #  Init writing  #
    ##################
    def __init_writing(self, file_path, structure_path, data, max_decimal, append):

        '''

        Declare and initialize variables for the writing process.

        Arguments
        =========
            file_path (str): path to data file to be writen
            structure_path (str): path to the structure file (how to read data file)
            data (Data object): object containing the data to be writen
            max_decimal (int): number of decimals for digits in scientific notation
            append (bool): If True, writing process will add to an existing file

        '''

        # Open output file
        if append:
            f = open(self._root_path+file_path, "a")
        else:
            f = open(self._root_path+file_path, "w")

        # Read the instructions on how to write the data file
        bloc, header, header_keys = self._create_bloc_structure(structure_path)

        # Prepare empty file if there is no data
        if data.nb_entries == 0:
            f.write("")

        # Return output file object
        return f, bloc


    ######################
    #  Reformat key pos  #
    ######################
    def __reformat_key_pos(self, structure):

        '''

        From an instruction structure line, reformat the quantity label
        and the output position so that any case can be passed to the
        generalized string generator functions.

        Argument
        ========
            structure (dict): one line from the structure sub-bloc

        '''

        # Declare the re-formatted quantities and positions
        keys = []
        positions = []

        # For each item in the structure dictionary ..
        for key, pos in structure.items():

            # Remove the $ONCE flag from the quantity name if necessary
            if "$ONCE" in key:
                keys.append(key.replace("$ONCE", ""))
            else:
                keys.append(key)

            # Add empty quantity location if originally not provided
            if isinstance(pos, tuple):
                positions.append(pos[1])
            else:
                positions.append(None)

        # Return formated structure instructions
        return keys, positions


    #########################
    #  Format str quantity  #
    #########################
    def __format_str_quantity(self, quantity, max_decimal):

        '''

        Take a quantity and return its string version, converting
        digits into scientific notation if needed.

        Arguments
        =========
            quantity (unknown): quantity from a data object (float, int, str, etc..)
            max_decimal (int): number of decimal points for floats in scientific notation

        '''

        # Return empty character if data not provided
        if quantity == None:
            return self.__empty_char

        # Do nothing if this is already a string
        if isinstance(quantity, (str, np.str_)):
            return quantity

        # Convert to string if this is an integer
        elif isinstance(quantity, (int, np.int_)):
            return str(quantity)

        # Return the scientific notation if this is a float
        elif self.__float_sci:
            if max_decimal <= 0:
                print("Error - Column width insufficient for digits in scientific notation.")
                return None
            sci_notation = "{:."+str(max_decimal)+"E}"
            return sci_notation.format(quantity)

        # Return normal float without formating if not in scientific notation
        else:
            return str(quantity)



    #####################
    #  Fill line space  #
    #####################
    def __fill_line_space(self, q, max_decimal):

        '''

        Take one or multiple quantities and return a string where
        each of the quantities are spaced with a " " and structured
        to the scientific notation if needed.

        Argument
        ========
            q (unknown): quantity from a data object (float, int, str, etc..)
            max_decimal (int): number of decimal points for floats in scientific notation

        '''

        # If the argument is a list of quantities ..
        if isinstance(q, (list,np.ndarray)):

            # Add each quantity one by one
            t_fill = ""
            for item in q:
                t_fill += self.__format_str_quantity(item, max_decimal) + self.__spacing

            # Remove the extra last space from the string
            t_fill = text[:-1]

        # If the argument is a single quantity ..
        else:

            # Copy the quantity directly
            t_fill = self.__format_str_quantity(q, max_decimal)

        # Return the formated line (string)
        return t_fill + "\n"


    ###################
    #  Generate line  #
    ###################
    def __generate_line(self, i_entry, keys, positions, d, max_decimal, i_list=None):

        '''

        Generate a line (str) for the output ascii file for a given
        data entry following a specific line structure.

        Arguments
        =========
            i_entry (int): current data entry index
            keys (list): list of quantities
            positions (list): list of column indexes for each quantity
            d (dict): data variable of a Data Interface object
            max_decimal (int): number of decimal points for floats in scientific notation
            i_list (int): if provided, current data array index within the $MULTILINE mode)

        '''

        # Return line if only one quantity with no position specified
        if len(keys) == 1 and positions[0] == None:
            quantity = self.__get_specific_quantity(keys[0], i_entry, i_list, d)
            return self.__format_str_quantity(quantity, max_decimal) + "\n"

        # Return line if positions are column indexes ..
        if isinstance(positions[0], int):
            return self.__generate_line_col(i_entry, keys, positions, \
                    d, max_decimal, i_list)

        # Return line if a single quantity should be listed on multiple columns ..
        if len(keys) == 1 and positions[0] == "split":
            return self.__generate_line_split(i_entry, keys, positions, \
                    d, max_decimal)

        # Return line if the positions are defined by character ranges ..
        if isinstance(positions[0], tuple):
            return self.__generate_line_char(i_entry, keys, positions, \
                    d, max_decimal, i_list)

        # Return nothing if structure is un-recognized ..
        print("Error - structure '", keys, positions, "' not recognized.")
        return None


    #######################
    #  Generate line col  #
    #######################
    def __generate_line_col(self, i_entry, keys, positions, d, max_decimal, i_list):

        '''

        Generate an output line string countaining data structured 
        by column indexes.

        Arguments
        =========
            i_entry (int): current data entry index
            keys (list): list of quantities
            positions (list): list of column indexes for each quantity
            d (dict): data variable of a Data Interface object
            max_decimal (int): number of decimal points for floats in scientific notation
            i_list (int): if provided, current data array index within the $MULTILINE mode)

        '''

        # Declare the output line
        line  = ""

        # Collect the maximum number of columns
        i_c_max = np.max(positions)

        # For each column in this output line
        for i_c in range(i_c_max+1):

            # If this column index is in the structure file ..
            if i_c in positions:

                # Find the structure key associated with this column
                key = keys[ positions.index(i_c) ]

                # Collect the targeted quantity
                quantity = self.__get_specific_quantity(key, i_entry, i_list, d)

                # Add data to the current output column
                line += self.__format_str_quantity(quantity, max_decimal) + self.__spacing

            # Add empty character if the column is not in the structure file
            else:
                line += self.__empty_char

        # Return the formated output line
        return utils.remove_last_spaces(line) + "\n"


    #########################
    #  Generate line split  #
    #########################
    def __generate_line_split(self, i_entry, keys, positions, d, max_decimal):

        '''

        Generate an output line string countaining a single quantity
        listed on multiple columns.

        Arguments
        =========
            i_entry (int): current data entry index
            keys (list): list of quantities
            positions (list): list of column indexes for each quantity
            d (dict): data variable of a Data Interface object
            max_decimal (int): number of decimal points for floats in scientific notation

        '''

        # Declare the output line
        line  = ""

        # Copy the key of the targeted quantity
        key = keys[0]

        # If the quantity is a list ..
        if isinstance(d[key][i_entry], (list, np.ndarray)):

            # Separate all items in the list by spaces
            for item in d[key][i_entry]:
                line += self.__format_str_quantity(item, max_decimal) + self.__spacing

        # Add quantity directly if not a list
        else:
            line += self.__format_str_quantity(d[key][i_entry], max_decimal)

        # Return the formated output line
        return utils.remove_last_spaces(line) + "\n"



    ########################
    #  Generate line char  #
    ########################
    def __generate_line_char(self, i_entry, keys, positions, d, max_decimal, i_list):

        '''

        Generate an output line string countaining data structured 
        by character index ranges.

        Arguments
        =========
            i_entry (int): current data entry index
            keys (list): list of quantities
            positions (list): list of column indexes for each quantity
            d (dict): data variable of a Data Interface object
            max_decimal (int): number of decimal points for floats in scientific notation
            i_list (int): if provided, current data array index within the $MULTILINE mode)

        '''

        # Collect the highest character index
        i_char_highest = -1
        for pos in positions:
            if pos[1] > i_char_highest:
                i_char_highest = pos[1]

        # Initialize the empty list of characters
        line_list = [" "] * (i_char_highest+1)

        # For each quantity in the structure line ..
        for key, pos in zip(keys, positions):

            # Copy its lower-bound character index
            i_char_min = pos[0]

            # Adjust decimal points in case not enough space
            md = min(max_decimal, pos[1]-i_char_min-6)

            # Collect the targeted quantity
            quantity = self.__get_specific_quantity(key, i_entry, i_list, d)

            # Collect the string to be incorporated in the current character range
            q_str = self.__format_str_quantity(quantity, md)

            # Find the upper-bound character index
            i_char_max = min(pos[1]+1, len(q_str)+i_char_min)

            # Assign each character to the output list of characters
            for i_char in range(i_char_min, i_char_max):
                line_list[i_char] = q_str[i_char-i_char_min]

        # Convert list of characters to a string
        line = ""
        for char in line_list:
            line += char

        # Return the formated 
        return line + "\n"


    ###########################
    #  Get specific quantity  #
    ###########################
    def __get_specific_quantity(self, key, i_entry, i_list, d):

        '''

        Return data for a specific quantity, entry, and array index if provided.

        Arguments
        =========
            key (str): quantity label
            i_entry (int): current data entry index
            i_list (int): if not None, array index of the current quantity
            d (dict): data dictionary of the Interface Data object

        '''

        # Collect quantity is the item is part of a list
        if isinstance(i_list, int):
            quantity = d[key][i_entry][i_list]
        
        # Collect quantity if it is not a list
        else:
            quantity = d[key][i_entry]

        # Return extracted quantity
        return quantity

