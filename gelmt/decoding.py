# decoding.py

# ------------------------------------------------------------------------------------------- #

# returns a list of strings, each string is a value of a datafield with the wanted tag

def get_controlfields(record, wanted_tag):
    collection = []
    
    for datafield in record: 
        datafield_tag = datafield.get('tag')
        
        if datafield_tag == wanted_tag: collection.append(datafield.text)
    
    return(collection)

# -------------------------------------------- #

# returns a list of dictionaries; every dictionary is a representation of a datafield with the wanted tag - the key / value pairs are the subfield_code / subfield_value pairs

def get_datafields(record, wanted_tag):
    collection = []
    
    for datafield in record: 
        datafield_tag = datafield.get('tag')
        
        if datafield_tag == wanted_tag:
            subfields = {}
            
            for subfield in datafield:
                subfield_code = subfield.get('code')
                subfield_value = subfield.text
                
                # if the subfield_code is already used in the subfield_dict, append the new value to the list with the old values
                if subfield_code in subfields: subfields[subfield_code].append(subfield_value)
                # else create a new entry with the subfield_code as key and the subfield_value as value
                else: subfields[subfield_code] = [subfield_value]

            if subfields: collection.append(subfields)
    
    return(collection)

# -------------------------------------------- #

# returns a list of strings; each string is a subfield_value of the wanted subfield code of the wanted datafield

def get_subfields(record, wanted_tag, wanted_code):
    # using a set so that there a no duplicate strings
    collection = set()
    
    for datafield in record: 
        datafield_tag = datafield.get('tag')
        
        if datafield_tag == wanted_tag:
            
            for subfield in datafield:
                subfield_code = subfield.get('code')
                
                if subfield_code == wanted_code: collection.add(subfield.text)

    return(list(collection))

# ------------------------------------------------------------------------------------------- #

# returns the id of a record as a string in a list, in case there is more than one id (which is not intended)

def get_id(record):
    return(get_controlfields(record, '001'))

# -------------------------------------------- #

# returns the contenttype of a record as a string in a list, in case there is more than one contenttype (which is not intended)

def get_contenttype(record):
    return(get_subfields(record, '336', 'a'))

# -------------------------------------------- #

# returns a list of dictionaries if possible else None
# 1. if there are authors in datafield with tag '100', they are returned
# 2. if there aren't, check for editors, which are treated as 'authors', when there is no author; 
# if found they are NOT returned, they only get returned by using the method get_editor()
# 3. if there are neither authors, nor editors, check for organisations which are then returned as authors

def get_author(record):
    datafields = get_datafields(record, '100')
    if datafields: return(datafields)
    # if there are editors, they count as author, but they are outputted with the function get_editor() not get_author()
    elif ("Herausgeber" in get_subfields(record, '700', 'e')) or ("Hrsg." in get_subfields(record, '700', 'e')): return
    else:
        datafields = get_datafields(record, '110')
        if datafields: return(datafields)

# -------------------------------------------- #

# returns a list of dictionaries with editors if the subfield value of the code 'e' of a datafield 
# with the tag '700' is either 'Herausgeber' or 'Hrsg.' else None

def get_editor(record):
    datafields = get_datafields(record, '700')

    if datafields: 
        editor_datafields = []
        for datafield_dict in datafields:
            if ('; '.join(datafield_dict['e']) == 'Herausgeber') or ('; '.join(datafield_dict['e']) == 'Hrsg.'):
                editor_datafields.append(datafield_dict)
        return(editor_datafields)

# -------------------------------------------- #

# returns the main title and remainder as TWO lists, in case there is more than one main title / title remainder (which is not intended)

def get_title(record):
    title_main = get_subfields(record, '245', 'a')
    title_remainder = get_subfields(record, '245', 'b')

    return(title_main, title_remainder)

# -------------------------------------------- #

# returns the edition as list

def get_edition(record):
    return(get_subfields(record, '250', 'a'))

# -------------------------------------------- #

def get_imprint(record):
    return(get_datafields(record, '264'))

# -------------------------------------------- #

def get_extent(record):
    subfields = get_subfields(record, '300', 'a')
    if subfields: 
        return(subfields)
    else:
        # sometimes instead of in field 300, there is information about the pages in field 773.g
        subfields = get_subfields(record, '773', 'g')
        for subfield in subfields:
            if 'pages' in subfield: return(subfield)
            # data sizes are in field 856.s
        else:
            subfields = get_subfields(record, '856', 's')
            if subfields: return(subfields)

# -------------------------------------------- #

def get_isbn(record):
    return(get_subfields(record, '020','a'))

# -------------------------------------------- #

def get_issn(record):
    return(get_subfields(record, '022','a'))

# -------------------------------------------- #

def get_lang(record):
    return(get_subfields(record, '041','a'))

# -------------------------------------------- #

def get_series(record):
    return(get_subfields(record, '490','a'))

# -------------------------------------------- #

def get_notes(record):
    return(get_subfields(record, '500', 'a'))

# -------------------------------------------- #

def get_lib_subject(record):
    # all tags between 600 and 655 except 653 (publisher) qualify as auto or int subjects
    set_without_pub = set(range(600, 655)) - set([653])
    
    subject_lib_datafields = []
    for num in set_without_pub:
        datafields = get_datafields(record, str(num))
        if datafields: subject_lib_datafields.extend(datafields)
            
    # 883 fields have information about auto subjects
    subject_auto_info_datafields = get_datafields(record, '883')
    
    return(subject_lib_datafields, subject_auto_info_datafields)

# -------------------------------------------- #

def get_pub_subject(record):
    return(get_subfields(record, '653', 'a'))    

# -------------------------------------------- #

# fields 82-84 can have ddc notations

def get_ddc_notation(record):
    datafields = get_datafields(record, '082')
    datafields += get_datafields(record, '083')
    datafields += get_datafields(record, '084')
    
    return(datafields)