# filtering.py

from lxml import etree
import re

# -------------------------------------------- #

# returns True if any value (of alues_to_match_with) that is matched to a passed list (values_to_match_on) is in the list

def bool_match(values_to_match_with, values_to_match_on):
    # if the lists are not empty, match
    if values_to_match_on and values_to_match_with:
        value_bools = []
        
        # iterate over values_to_match_with to match every value of it with the values_to_match_on list
        for value in values_to_match_with:
            
            # append True, if there is a match, otherwise append False
            if value in values_to_match_on: value_bools.append(True)
            else: value_bools.append(False)

        # if any passed value of values_to_match_with is matched True, return True
        return(boolean is True for boolean in value_bools)

    # one or both lists are is empty, no match possible
    else: return(False)

# -------------------------------------------- #

# returns True if an int or auto subject is found

def check_if_subject(record):
    for datafield in record:
        datafield_tag = datafield.get('tag')

        # all tags between 600 and 655 except 653 qualify as auto or int subjects
        if datafield_tag == '653': continue
        # check first if tag is not None, otherwise there can be a 'TypeError' when using int()
        elif (datafield_tag != None) and (600 <= int(datafield_tag) <= 655): return(True)    

# -------------------------------------------- #

# returns a list of ids of a xml with a specific structure = structure of the old corpus

def get_id_list(filepath):
    ids = []
    # lxml does not allow the use of variables for "tag=''" or attrib[''], so they have to be changed in the function itself, if wanted
    for event, record in etree.iterparse(filepath, tag="doc"):
        # oftentimes the ids of the old corpus have a zero at the beginning, 
        # but the ids in the marcxml have not, so the ids are stripped of these zeros
        for datafield in record:
            if datafield.attrib['name'] == 'id': ids.append(re.sub('^0', '', datafield.text))
                
    return(ids)