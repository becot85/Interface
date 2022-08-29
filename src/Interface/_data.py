'''

    Creation date: October 8th, 2021
    Contributors: Benoit Cote (cotebenoit8@gmail.com)

'''

# Import Python packages
import numpy as np
import copy

# Import Interface toolkit
from . import interface_utils as utils


# Declare the class
class data( object ):

    '''

    This is a data class containing the common functions and 
    attributes shared by any type of input nuclear data file.

    Attributes
    ==========
        quantities (list): quantities extracted from the file (e.g. Z, A, reaction,..)
        data (dictionary): list all entries in the file, for the targeted quantity (dict. key)
        nb_quantities (int) : total number of quantities
        nb_entries (int): total number of entries

    Functions
    =========
        set_data: assign an input data dictionary
        filter_data: return data object given sets of constraints (filters)
        get_quantities: return quantities arrays given sets of constraints
        print_quantities: same as get_quantities, but a printed version on your screen

    '''

    #################################
    #  Initialization of the class  #
    #################################
    def __init__(self, data=dict()):

        '''

        Initialize the data class

        Arguments
        =========
            data: data dictionary originating from an input data file 
                  that has already been read.

        '''

        # Initialize the data dictionaty
        self.set_data(data)

        # Define what should be log(zero)
        self.__log_zero = -99.0



    ##############
    #  Set data  #
    ##############
    def set_data(self, data):
        
        '''

        Overwrite (or initialize) the data dictionary

        Arguments
        =========
            data: data dictionary originating from an input data file 
                  that has already been read.

        '''

        # Overwrite and read dictionary keys
        self.data = data
        self.__collect_data_quantities()

        # Set lists to NumPy arrays
        for i_entry in range(self.nb_entries):
            for quantity in self.data:
                if isinstance(self.data[quantity][i_entry], list):
                    self.data[quantity][i_entry] = np.array(self.data[quantity][i_entry])

        # Create entries for un-logged (10**) values if needed
        self.__unlog_values()



    #############################
    #  Collect data quantities  #
    #############################
    def __collect_data_quantities(self):
        
        '''

        Store the keys of the data dictionary

        '''

        # Declare the list of all quantities present in the data
        self.quantities = []

        # Read and save quantity names
        for q in self.data:
            self.quantities.append(q)

        # Keep in memory the size of the dictionary
        self.nb_quantities = len(self.quantities)
        if self.nb_quantities == 0:
            self.nb_entries = 0
        else:
            self.nb_entries = len(self.data[q])

        # Find which quantities are digits
        self.__find_digits()



    #################
    #  Find digits  #
    #################
    def __find_digits(self):

        '''

        Find and keep in memory all self.data quantities that are digits.
        In case the quantity refers to an array, it will be flagged as 
        a digit quantity if all items in the array are digits (with the
        exception of None).

        '''

        # Declare the list of digit quantities
        self.__digit_q_list = []

        # For each quantity in the data dictionary ..
        for q in self.quantities:

            # Initially assume that this is a digit quantity
            is_digit = True

            # For each data entry ..
            for i_entry in range(self.nb_entries):

                # Switch is_digit to False if a non-digit item is detected
                if isinstance(self.data[q][i_entry], (list, np.ndarray)):
                    for item in self.data[q][i_entry]:
                        if not isinstance(item, (int, float, type(None))):
                            is_digit = False
                elif not isinstance(self.data[q][i_entry], (int, float, type(None))):
                    is_digit = False

                # Exit the "for i_entry" loop if needed
                if not is_digit:
                    continue

            # Mark the quantity as a digit if needed
            if is_digit:
                self.__digit_q_list.append(q)



    ###################
    #  Unlogs values  #
    ###################
    def __unlog_values(self):
        
        '''

        Scan through the self.data dictionary, and create an entry
        with an un-logged version of every "log_.." quantity. This
        function assumes that all lists in self.data are numpy
        arrays already.

        '''

        # Keep track of whether an un-logged quantity has been created
        new_quantities = False

        # For every digit "log_.." quantity in the data dictionary ..
        for q in self.quantities:
            if len(q) >= 5 and q in self.__digit_q_list:
                if q[:4] == "log_":

                    # If the un-logged quantity does not already exist ..
                    q_unlog = q[4:]
                    if not q_unlog in self.quantities:

                        # Switch on flag annoncing that the data have been modified
                        new_quantities = True

                        # Create dictionary entry for the un-logged quantities
                        self.data[q_unlog] = []
                        for i_entry in range(self.nb_entries):
                            self.data[q_unlog].append(self.__unlog_specific_item(self.data[q][i_entry]))

        # Re-collect quantities if needed
        if new_quantities:
            self.__collect_data_quantities()


    #########################
    #  Unlog specific item  #
    #########################
    def __unlog_specific_item(self, item):

        '''

        Take an item (digit or a list of digits) and return its un-logged
        version (10**), assuming it is already given in log.

        Argument
        ========
            item (digit or list of digits): values to be un-logged

        '''

        # Make a copy of the item to avoid linked variable
        new_item = copy.deepcopy(item)

        # Un-log directly if not an array
        if isinstance(item, (int, float)):
            new_item = 10**(item)

        # If item is an array ..
        if isinstance(item, (list, np.ndarray)):

            # Unlog each digit in the array
            for i_item in range(len(item)):
                if isinstance(item[i_item], (int, float)):
                    new_item[i_item] = 10**(item[i_item])

            # Make sure item is a numpy array
            new_item = np.array(new_item)

        # Return the un-logged version of the input item
        return new_item


    #################
    #  Filter data  #
    #################
    def filter_data(self, conditions=None):

        '''

        Return a filtered Data object following a given a set of conditions.

        Argument
        ========
            conditions (string or list): list of conditions to filter data

        '''

        # TODO make function that looks over all reasons we would like to return self of empty

        # Return empty data object if there is nothing to filter
        if self.nb_entries == 0:
            return data(data=dict())

        # Return self if there is no conditions to be applied
        if conditions == None:
            return self

        # Reformat the input structure
        conditions = self.__str_to_list(conditions)
        if not isinstance(conditions, (list, np.ndarray)):
            print("Error - conditions must be a string or a list of strings.")
            return self

        # Get the operator and the left- and right-hand sides of each condition
        left_list, operator_list, right_list = self.__organize_conditions(conditions)
        if left_list == None:
            return self

        # Check whether the left and right sides are available
        if self.__sides_dont_exist(left_list, operator_list, right_list):
            return self

        # Declare the filtered Data object
        new_data = dict()
        for key in self.quantities:
            new_data[key] = []

        # For each entry in the file ..
        for i_entry in range(self.nb_entries):

            # Declare the booleans that will define whether all conditions are satisfied 
            bool_single = True
            bool_list = []

            # For each condition outcome ..
            for left, operator, right in zip(left_list, operator_list, right_list):
                outcome = self.__apply_operator(left, operator, right, i_entry)

                # If the outcome is a list of booleans, store the list
                if type(outcome) == np.ndarray:
                    bool_list.append(outcome)

                # Exit if something went wrong
                elif outcome == None:
                    return self

                # If the condition is not satisfied, move to the next entry
                elif outcome == False:
                    bool_single = False
                    break

            # If there is a chance that the entry satisfies all conditions
            if bool_single:

                # Copy the entire entry if there are no boolean list
                len_bool_list = len(bool_list)
                if len_bool_list == 0:
                    for key in self.quantities:
                        new_data[key].append(self.data[key][i_entry])

                # If boolean list(s) is(are) provided ..
                else:

                    # Combine boolean lists
                    bool_combined = bool_list[0]
                    len_bool_combined = len(bool_combined)
                    for i_b in range(1, len_bool_list):
                        if len(bool_list[i_b]) == len_bool_combined:
                            bool_combined *= bool_list[i_b]
                        else:
                            print("Error - Boolean lists are not the same size.")
                            return self

                    # If there are anything that respect all conditions ..
                    if True in bool_combined:

                        # For each quantity ..
                        for key in self.quantities:

                            # Copy the entry part that is not a list
                            if not type(self.data[key][i_entry]) == np.ndarray:
                                new_data[key].append(self.data[key][i_entry])

                            # Copy the entry part that is not a list of relevant length
                            elif not len(self.data[key][i_entry]) == len_bool_combined:
                                new_data[key].append(self.data[key][i_entry])

                            # If this quantity is a list of relevant length ..
                            else:

                                # Only add values if conditions are respected
                                new_data[key].append([])
                                for i_b in range(len_bool_combined):
                                    if bool_combined[i_b]:
                                        new_data[key][-1].append(self.data[key][i_entry][i_b])

        # Create and return the filtered data object
        return data(data=new_data)



    ####################
    #  Get Quantities  #
    ####################
    def get_quantities(self, quantity_list, conditions=None):

        '''

        Return a multi-D array of given quantities from the data, accounting
        for filtering conditions if provided. The returned array will be of
        the form [ entry index ][ quantity index ].

        Arguments
        =========
            quantity_list (str or list): Quantity(ies) that need to be returned
            conditions (string or list): list of conditions to filter data

        '''

        # Reformat the input structure
        quantity_list = self.__str_to_list(quantity_list)

        # Check whether the requested quantities exist
        if self.__quantities_dont_exist(quantity_list):
            return None

        # Filter data if needed
        if conditions == None:
            data_temp = self
        else:
            data_temp = self.filter_data(conditions=conditions)
            if data_temp == dict():
                return None

        # Declare the list of quantities to be returned
        q_return = []
        
        # For each entry in the (possibly filtered) data ..
        for i_entry in range(data_temp.nb_entries):

            # Collect the value of each requested quantity
            q_return.append([])
            for quantity in quantity_list:
                q_return[i_entry].append(data_temp.data[quantity][i_entry])

        # Return the quantities
        return q_return



    ######################
    #  Print Quantities  #
    ######################
    def print_quantities(self, quantity_list, conditions=None, nb_print_max=1000):

        '''

        Print the value of given quantities from the data, accounting for 
        filtering conditions if provided. This is a more-visual version of
        the get_quantities function. It will not return a multi-D array.

        Arguments
        =========
            quantity_list (str or list): Quantity(ies) that need to be returned
            conditions (string or list): list of conditions to filter data
            nb_print_max (int): maximmum number of entries that can be printed

        '''

        # Reformat the input conditions
        if conditions == None:
            nb_conditions = 0
        else:
            conditions = self.__str_to_list(conditions)
            nb_conditions = len(conditions)

        # Gather the quantities in an array form
        q = self.get_quantities(quantity_list, conditions)
        if q == None:
            return
        nb_q = len(q)

        # If there is something to print ..
        if nb_q > 0:

            # Print statistics
            if nb_conditions == 0:
                print(nb_q,"entries")
            else:
                if nb_conditions > 1:
                    cc = "conditions"
                else:
                    cc = "condition"
                print(nb_q,"out of",self.nb_entries,"entries met the following",cc)
                for cond in conditions:
                    print("  --> ",cond)

            # Reformat the input structure
            quantity_list = self.__str_to_list(quantity_list)
            len_quantity_list = len(quantity_list)

            # Plan spacing if entrise are to be listed without space in between
            if len_quantity_list == 1:
                print()

            # For each entry ..
            for i_entry in range(nb_q):

                # Add spacing in between entries if needed
                if len_quantity_list > 1:
                    print()

                # Print quantities with their label
                for i_q in range(len_quantity_list):
                    print(quantity_list[i_q]+": ",q[i_entry][i_q])

                # Stop if too many entries were printed
                if i_entry == nb_print_max - 1:
                    print("... not all entries were shown (see nb_print_max parameter).")
                    break



    #################
    #  Str to List  #
    #################
    def __str_to_list(self, string):

        '''

        Include the input string into a list, if not already a list,
        and return it.

        Argument
        ========
            string: either a list, or an actual string

        '''

        # Add the string in a list if necessary
        if isinstance(string, str):
            string = [string]

        # Return the list
        return string


    #########################
    #  Organize Conditions  #
    #########################
    def __organize_conditions(self, condition_list):

        '''

        Take a list of conditions, and split them into their left-hand 
        side, opetator, and right-hand side.

        Argument
        ========
            condition_list (list of str): list of conditions to filter data

        '''

        # Declare the lists to be returned
        left_list = []
        operator_list = []
        right_list = []

        # For each condition ..
        for c in condition_list:

            # Clean and remove extra spaces
            condition = utils.remove_extra_spaces(c)

            # Find the operator that will split the left and right sides
            operator = self.__get_operator(condition)

            # Add nothing to the lists if no single operator was found
            if operator == None:
                left_list.append(None)
                operator_list.append(None)
                right_list.append(None)

            # If a single operator was found ..
            else:

                # Add spaces for "in" and "not in" to correctly split condition
                # Ex: "k in string" should split ["k","string"], not ["k","str","g"]
                if operator == "in":
                    operator = " in "
                elif operator == "not in":
                    operator = " not in "

                # Split the condition using the operator 
                split = condition.split(operator)

                # Restore operator's name
                if operator == " in ":
                    operator = "in"
                elif operator == " not in ":
                    operator = "not in"

                # Error message if one side of the condition is missing
                if not len(split) == 2:
                    print("Error - Side(s) missing in",c)
                    left_list.append(None)
                    operator_list.append(None)
                    right_list.append(None)

                # Fill the list if everything is ok
                else:
                    left_list.append(utils.remove_extra_spaces(split[0]))
                    operator_list.append(operator)
                    right_list.append(utils.remove_extra_spaces(split[1]))

        # Return None if there was a problem
        if None in left_list:
            return None, None, None

        # Return the organized conditions
        return left_list, operator_list, right_list



    ############################
    #  Quantities Don't Exist  #
    ############################
    def __quantities_dont_exist(self, quantity):

        '''

        Return True is a given set of quantities are not
        in the list of the data dictionary keys.

        Argument
        ========
            quantity (list of str): list of quantities

        '''

        # Set initially that quantities do exist
        dont_exist = False

        # For each quantity in the list ..
        for q in quantity:

            # Print error if the quantity is not available
            if not q in self.quantities:
                print("Error -", q, "is not an available quantity.")
                dont_exist = True

        # Return whether the quantities are all available
        return dont_exist



    ##################
    #  Get Operator  #
    ##################
    def __get_operator(self, condition):

        '''

        Take a condition, and find the operator that will split
        the left- and right-hand sides of the condition.

        Argument
        ========
            condition (str): condition to filter data

        '''

        # Declare the list of found operators
        op_found = []

        # Look for special cases for in and not-in
        if " not in in " in condition or " in not in " in condition:
            op_found.append("not in")
            op_found.append("in")
        elif " not in not in " in condition:
            op_found.append("not in")
            op_found.append("not in")
        elif " in in " in condition:
            op_found.append("in")
            op_found.append("in")

        # Look for in and not-in operators
        else:
            op_found = self.__add_operator(condition, " not in ", op_found)
            op_found = self.__add_operator(condition, " in ", op_found, exclude=[" not "])

        # Look for != operator
        op_found = self.__add_operator(condition, "!=", op_found)

        # Look for >= operator
        op_found = self.__add_operator(condition, ">=", op_found)

        # Look for <= operator
        op_found = self.__add_operator(condition, "<=", op_found)

        # Look for = operator
        op_found = self.__add_operator(condition, "=", op_found, exclude=["!=",">=","<="])

        # Look for > operator
        op_found = self.__add_operator(condition, ">", op_found, exclude=[">="])

        # Look for < operator
        op_found = self.__add_operator(condition, "<", op_found, exclude=["<="])

        # Error if no operator was found
        if len(op_found) == 0:
            print("Error - No operator was found in:", condition)
            print("  Valid operators are [=, !=, >=, >, <=, <, in, not in].")
            return None

        # Error if more than one operator were found
        if len(op_found) > 1:
            clean_op = []
            for op in op_found:
                if not op in clean_op:
                    clean_op.append(op)
            print("Error - Too many operators", clean_op, "were found in",condition)
            return None

        # Return the one operator if everything went well
        return op_found[0]


    #######################
    #  Sides Don't Exist  #
    #######################
    def __sides_dont_exist(self, left_list, operator_list, right_list):

        '''

        Check whether a list of conditions can be applied.

        Arguments
        =========
            left_list (list): left-hand side of a condition
            operator_list (list): operator in between the left and right sides
            right_list (list): right-hand side of a condition

        '''

        # Declare whether sides exist
        dont_exist = False

        # For each condition ..
        for left, operator, right in zip(left_list, operator_list, right_list):

            # If the condition is either in or not-in ..
            if operator in ["in", "not in"]:

                # Check whether the right side is available
                # Do not return yet, since we want the full list of errors
                if not right in self.quantities:
                    print("Error -",right,"is not available.")
                    dont_exist = True

            # If the condition involves a math operator ..
            else:

                # Check whether the left side is available
                if not left in self.quantities:
                    print("Error -",left,"is not available.")
                    dont_exist = True

                # Check whether the right side is a digit
                try:
                    test = float(right)
                except:
                    print("Error -",right,"should be a digit in",left,operator,right)
                    dont_exist = True

        # Return whether sides exist
        return dont_exist



    ##################
    #  Add Operator  #
    ##################
    def __add_operator(self, condition, op, op_found, exclude=[]):

        '''

        Take a condition, and add the targeted operator in a given list
        of operators each time it is found in the condition.

        Arguments
        =========
            condition (str): condition for filtering data
            op (str): targeted operator 
            op_found (list of str): operators that were previously found
            exclude (list of str): operators (e.g. !=) that may include op (e.g. =)

        '''

        # If the targeted operator is in the condition ..
        if op in condition:

            # Get the number of times the targeted operator appears
            nb_op = condition.count(op)

            # Get the nummber of times the excluded operators appear
            nb_exclude = 0
            for op_ex in exclude:
                nb_exclude += condition.count(op_ex)

            # Add the targeted operator each time it appears by its own
            for i in range(max(0, nb_op-nb_exclude)):
                op_found.append(utils.remove_extra_spaces(op))

        # Return the updated list of found operators
        return op_found



    ####################
    #  Apply Operator  #
    ####################
    def __apply_operator(self, left, operator, right, i_entry):

        '''

        Return True or False (or list) depending on whether the condition
        "left operator right" is satisfied. This could be "T < 1e3",
        "ne22 in reaction", "reaction = li8 he4 he4", etc.

        Arguments
        =========
            left (str): left-hand side of the condition
            operator (str): operator for the condition (e.g. =, <, not in)
            right (str): right-hand side of the condition
            i_entry (index): entry index in the data

        '''

        # Equal operator ..
        if operator == "=":
            return self.data[left][i_entry] == float(right)

        # If not-equal operator ..
        if operator == "!=":
            return self.data[left][i_entry] != float(right)

        # If greater-than-or-equal operator ..
        if operator == ">=":
            return self.data[left][i_entry] >= float(right)

        # If greater-than operator ..
        if operator == ">":
            return self.data[left][i_entry] > float(right)

        # If less-than-or-equal operator ..
        if operator == "<=":
            return self.data[left][i_entry] <= float(right)

        # If less-than operator ..
        if operator == "<":
            return self.data[left][i_entry] < float(right)

        # If in operator:
        if operator == "in":
            return self.__apply_in_operator(left, operator, right, i_entry)

        # If not-in operator:
        if operator == "not in":
            return not self.__apply_in_operator(left, operator, right, i_entry)

        # Return an error if the operator is not valid
        print("Error -", operator, "is not a valid operator.")
        print("  Valid operators are [=, !=, >=, >, <=, <, in, not in].")
        return False


    #######################
    #  Apply in Operator  #
    #######################
    def __apply_in_operator(self, left, operator, right, i_entry):

        '''

        Return True or False depending on whether left is in right.

        Arguments
        =========
            left (str): left-hand side of the condition
            operator (str): operator for the condition (e.g. =, <, not in)
            right (str): right-hand side of the condition
            i_entry (index): entry index in the data

        '''

        # Return the condition if the target quantity is a string
        if isinstance(self.data[right][i_entry], str):
            return left in self.data[right][i_entry]

        # If the quantity is a list ..
        if isinstance(self.data[right][i_entry], (list, np.ndarray)):

            # Return False if the list is empty
            if len(self.data[right][i_entry]) == 0:
                return False

            # Convert the left side into a digit is the list does not include str
            if type(self.data[right][i_entry][0]) == str:
                new_left = left
            else:
                new_left = float(left)

            # Return the condition
            return new_left in self.data[right][i_entry]

        # Error message if things are inconsistent
        print("Error - ",right,"must either be a string, a list of strings, or a list of digits.")
        return None
