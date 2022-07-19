'''

    Creation date: July 2022
    Contributors: Benoit Cote (cotebenoit8@gmail.com)

    Various tools (functions) used by Interface

'''


###########################
#  Remove initial spaces  #
###########################
def remove_initial_spaces(string):

    '''

    Take a string, and return the same string, but without empty
    spaces at the begining (e.g. "  the text " --> "the text ")

    Argument
    ========
        string (str): string for which spaces need to be removed

    '''

    # Return the same if the string is empty
    if len(string) == 0:
        return string

    # Find the first instance of a non-space character
    i_start = 0
    while string[i_start] == " ":
        i_start += 1
        if i_start == len(string):
            break

    # Return the cleaned string
    return string[i_start:]


#########################
#  Remove extra spaces  #
#########################
def remove_extra_spaces(string):

    '''

    Remove extra spaces of a given string

    Argument
    ========
        string: single input string

    '''

    # Remove extra spaces at the begining
    string = remove_initial_spaces(string)
    len_string = len(string)

    # Cases where no more operation is needed
    if len_string == 0 or len_string == 1:
        return string

    # Declare the string that will replace the input string
    new_str = ""

    # Scan through each character, and skip extra spaces
    for i_c in range(0, len_string):
        if not (string[i_c] == " " and string[i_c-1] == " "):
            new_str += string[i_c]

    # Remove the last space if any
    if new_str[-1] == " ":
        new_str = new_str[:-1]

    # Return the new string the input string
    return remove_initial_spaces(new_str)


#######################
#  Remove all spaces  #
#######################
def remove_all_spaces(string):

    '''

    Remove all spaces of a given string.

    Argument
    ========
        string: single input string

    '''

    # Return the new string without space
    return string.replace(" ","")

