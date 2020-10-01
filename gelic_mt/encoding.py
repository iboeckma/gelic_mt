# encoding.py

import unicodedata

# -------------------------------------------- #

# pass a value: str / list of strings / list of dicts; if it is a string or a list of strings, return the passed value
# if it is a list of dicts, return a list of strings -> each string contains the values of a dict, separated by ' -- '
# also, every string that is returned is transformed from nfd to nfc

def json_encode(thing_to_encode):
    encoded_list = []
    if type(thing_to_encode) is list:
        for item in thing_to_encode:
            
            if type(item) is dict:
                counter = 0
                encoded_dict = ""
                for key, value in item.items():
                    # don't add " -- " before a value if it is the first value of a dict
                    if counter == 0:
                        encoded_dict += str(value)
                        counter += 1
                    # separate the different information of a dict with ' -- '
                    else: 
                        encoded_dict += " -- " + str(value)
                encoded_list.append(unicodedata.normalize('NFC', encoded_dict))
            
            elif type(item) is str: encoded_list.append(unicodedata.normalize('NFC', item))
    elif type(thing_to_encode) is str: return(unicodedata.normalize('NFC', thing_to_encode))
    
    if encoded_list: return(encoded_list)