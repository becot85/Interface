'''

    Creation date: October 8th, 2021
    Contributors: Benoit Cote (cotebenoit8@gmail.com)

'''

# Import Python packages
import numpy as np


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
        search_data: return data given sets of constraints (filters)

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

        # Set arrays to NumPy arrays
        for i_entry in range(self.nb_entries):
            for quantity in self.data:
                if type(self.data[quantity][i_entry]) == list:
                    self.data[quantity][i_entry] = np.array(self.data[quantity][i_entry])



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

        # Renormalize the input structure
        if type(conditions) == str:
            conditions = [conditions]
        elif not (type(conditions) == list or type(conditions) == np.ndarray):
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

        Return a list of given quantities from the data, accounting
        for filtering conditions if provided.

        Arguments
        =========
            quantity_list (str or list): Quantity(ies) that need to be returned
            conditions (string or list): list of conditions to filter data

        '''

        # Renormalize the input structure
        if type(quantity_list) == str:
            quantity_list = [quantity_list]

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
        for i_entry in range(data_temp.nb_entries)-1:

            # Collect the value of each requested quantity
            q_return.append([])
            for quantity in quantity_list:
                q_return[i_entry].append(data_temp.data[quantity][i_entry])

        # Return the quantities
        return q_return



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
            condition = self.__clean_spaces(c)

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
                    left_list.append(self.__clean_spaces(split[0]))
                    operator_list.append(operator)
                    right_list.append(self.__clean_spaces(split[1]))

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


    ##################
    #  Clean Spaces  #
    ##################
    def __clean_spaces(self, string):

        '''

        Take a string and remove extra spaces from it.

        Argument
        ========
            string (str): string that may include extra spaces

        '''

        # Return nothing if the string is empty
        if string == "":
             return string

        # Declare the cleaned string
        len_string = len(string)
        string_new = ""

        # Skip the initial spaces
        i_start = 0
        while string[i_start] == " ":
            i_start += 1
            if i_start == len_string:
                return ""

        # Add the first character to the cleaned string
        string_new += string[i_start]

        # For each remaining character in the string ..
        for i_char in range(i_start+1, len_string):

            # Only add the character if it is not a double space
            if not (string[i_char] == " " and string[i_char-1] == " "):
                string_new += string[i_char]

        # Return the cleaned string
        if string_new[-1] == " ":
            return string_new[:-1]
        else:
            return string_new



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
                op_found.append(self.__clean_spaces(op))

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
