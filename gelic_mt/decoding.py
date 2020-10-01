# decoding.py

# ------------------------------------------------------------------------------------------- #

# returns the value of the first controlfield with the wanted tag as string

def get_controlfield(record, wanted_tag):
    for datafield in record: 
        datafield_tag = datafield.get('tag')
        
        if datafield_tag == wanted_tag: return(datafield.text)

# -------------------------------------------- #

# returns a list of dictionaries; every dictionary is a representation of a datafield with the wanted tag - the key / value pairs are the subfield_code / subfield_value pairs

def get_datafields(record, wanted_tag):
    collection = []
    
    for datafield in record: 
        datafield_tag = datafield.get('tag')
        
        if datafield_tag == wanted_tag:
            subfields = {}

            # indicator fields are not repeatable, so it's safe to just append them here
            subfields['ind1'] = datafield.get('ind1')
            subfields['ind2'] = datafield.get('ind2')
            
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
    # using a set so that there are no duplicate strings
    collection = set()
    
    for datafield in record: 
        datafield_tag = datafield.get('tag')
        
        if datafield_tag == wanted_tag:
            
            for subfield in datafield:
                subfield_code = subfield.get('code')
                
                if subfield_code == wanted_code: collection.add(subfield.text)

    return(list(collection))

# ------------------------------------------------------------------------------------------- #

# returns the id of a record as a string

def get_id(record):
    return(get_controlfield(record, '001'))

# -------------------------------------------- #

# returns the contenttypes of a record as strings in a list

def get_contenttype(record):
    return(get_subfields(record, '336', 'a'))

# -------------------------------------------- #

# returns a list of dictionaries if possible else None
# 1. if there are authors in datafield with tag '100', they are returned
# 2. if there aren't, check for editors, which are treated as 'authors', when there is no author; 
# if found they are NOT returned, they only get returned by using the method get_editor()
# 3. if there are neither authors, nor editors, check for organisations which are then returned as authors

def get_author(record):
    aut_datafields = get_datafields(record, '100')
    role_datafields = get_datafields(record, '700')
    # if there are editors, they count as author, but they are outputted with the function get_editor() not get_author()
    editor = False
    for d in role_datafields:
        # if there is more than one author, the other authors are handled with field 700
        try: 
            if "aut" in d.get('4'): aut_datafields.append(d)
            elif "edt" in d.get('4'): editor = True
        except TypeError: continue
    if aut_datafields: return(aut_datafields)
    elif editor == True: return
    # if there are no authors in fields 100 and 700 and no editors: organisation should be handled as author
    else:
        org_datafields = get_datafields(record, '110')
        return(org_datafields)

# -------------------------------------------- #

# returns a list of dictionaries with editors if the subfield value of the code 'e' of a datafield 
# with the tag '700' is either 'Herausgeber' or 'Hrsg.' else None

def get_editor(record):
    role_datafields = get_datafields(record, '700')

    if role_datafields: 
        edit_datafields = []
        for role_dict in role_datafields:
            role = get_subfields(record, '700', 'e')
            if role:
                if ("Herausgeber" in role) or ("Hrsg." in role): edit_datafields.append(role_dict)
        return(edit_datafields)

# -------------------------------------------- #

# returns the main title and remainder as TWO lists, in case there is more than one main title / title remainder (which is not intended)

def get_title(record):
    title_main = get_subfields(record, '245', 'a')
    title_remainder = get_subfields(record, '245', 'b')

    return(title_main, title_remainder)

# -------------------------------------------- #

# returns the edition fields of a record as strings in a list

def get_edition(record):
    return(get_subfields(record, '250', 'a'))

# -------------------------------------------- #

# returns the fields relevant for the imprint of a record as dicts in a list

def get_imprint(record):
    return(get_datafields(record, '264'))

# -------------------------------------------- #

# returns the extent fields of a record as strings in a list

def get_extent(record):
    ext_subfields = get_subfields(record, '300', 'a')
    if ext_subfields: return(ext_subfields)
    else:
        # sometimes instead of in field 300, there is information about the pages in field 773.g
        subfields = get_subfields(record, '773', 'g')
        for subfield in ext_subfields:
            if 'pages' in subfield: return(subfield)
            # data sizes are in field 856.s
        else:
            subfields = get_subfields(record, '856', 's')
            if subfields: return(subfields)

# -------------------------------------------- #

# returns the isbn fields of a record as strings in a list

def get_isbn(record):
    return(get_subfields(record, '020','a'))

# -------------------------------------------- #

# returns the issn fields of a record as strings in a list

def get_issn(record):
    return(get_subfields(record, '022','a'))

# -------------------------------------------- #

# returns the language fields of a record as strings in a list

def get_lang(record):
    return(get_subfields(record, '041','a'))

# -------------------------------------------- #

# returns the series fields of a record as strings in a list

def get_series(record):
    return(get_subfields(record, '490','a'))

# -------------------------------------------- #

# returns the notes fields of a record as strings in a list

def get_notes(record):
    return(get_subfields(record, '500', 'a'))

# -------------------------------------------- #

# returns the fields that are relevant for the indexed librarian subject terms (automatic or intellectual) of a record as
# two lists of dictionaries - one wth the subject index terms and one with provenance information
# the latter only has information for automatic terms at the moment

def get_subject_lib(record):
    # all tags between 600 and 655 except 653 (vlb = publisher) but also 689 qualify as auto or int subjects
    set_without_vlb = set(range(600, 656)) - set([653])
    set_without_vlb.add(689)
    
    subject_lib_datafields = []
    for tag in set_without_vlb:
        datafields = get_datafields(record, str(tag))
        if datafields: subject_lib_datafields.extend(datafields)
            
    # 883 fields have information about the provenance of subjects
    subject_provenance_datafields = get_datafields(record, '883')

    return(subject_lib_datafields, subject_provenance_datafields)

# -------------------------------------------- #

# returns the fields that contain vlb subject terms of a record as strings in a list

def get_subject_vlb(record):
    return(get_subfields(record, '653', 'a'))    

# -------------------------------------------- #

# returns the ddc notation fields as dicts in a list

def get_ddc_notation(record):
    # fields 82-84 can have ddc notations
    datafields = get_datafields(record, '082')
    datafields += get_datafields(record, '083')
    datafields += get_datafields(record, '084')
    
    return(datafields)