# transforming.py

# fields that are not transformed at the moment: edition, isbn, issn, lang, notes
# possibilities: return only isbn13 if possible, else return another isbn

import re

# ------------------------------------------------------------------------------------------- #

# returns passed value as string
# if there is more than one value in the passed list, the items are separated by ';'
# used for: id, contenttype, extent, series 

def transform_to_string(list_or_string):
	if type(list_or_string) is str: return(list_or_string)
	elif type(list_or_string) is list: return('; '.join(list_or_string))

# -------------------------------------------- #

# returns a list of dictionaries with persons or None
# a dictionary contains the name of the person and an id (ORCID or GND-ID) if possible

def transform_person(person_datafields, role = 'person'):
    persons = []
    if person_datafields:
        for datafield_dict in person_datafields:
            person = {}
            if 'a' in datafield_dict: person[role + '_name'] = '; '.join(datafield_dict['a'])
            if '0' in datafield_dict: person[role + '_id'] = datafield_dict['0'][0]
            if person: persons.append(person)
        if persons: return(persons)

# -------------------------------------------- #

# returns the main title and remainder as a string, separated by ' : '
# if there is more than one main title (which is not intended), they are separated by ' ; '
# if there is more than one title remainder they are already separated by ' ; ' 
# but in the case of a stray title remainder, they are also added separated by ' ; ' by the method

def transform_title(title_main, title_remainder):
    if title_main:
        if title_remainder: return(' ; '.join(title_main) + ' : ' + ' ; '.join(title_remainder))
        else: return('; '.join(title_main))
    else: print('no title')

# -------------------------------------------- #

# returns the imprint, if all parts (publication_place, publisher, publication_date) were found

def transform_imprint(imprint_datafields):
    imprints = []
    if imprint_datafields:
        for datafield_dict in imprint_datafields:
            imprint = {}
            if 'a' in datafield_dict: imprint['publication_place'] = '; '.join(datafield_dict['a'])
            if 'b' in datafield_dict: imprint['publlisher'] = '; '.join(datafield_dict['b'])
            if 'c' in datafield_dict: imprint['publication_date'] = '; '.join(datafield_dict['c'])

            if ('publication_place' in imprint) and ('publisher' in imprint) and ('publication_date' in imprint): 
            	imprints.append(publication_place + ': ' + publisher + ', ' + publication_date)

    return(imprints)

# -------------------------------------------- #

def transform_lib_subject(subject_lib_datafields, subject_auto_info_datafields):
    subject_auto = []
    subject_int = []

    if subject_lib_datafields:
	    for datafield_dict in subject_lib_datafields:
	        
	        # only auto subjects have the datafield_dict key '8'
	        try:
	            datafield_dict['8']
	            subject = {}
	            for info_dict in subject_auto_info_datafields: 
	                for k, v in info_dict.items():
	                    # if the value of info_dict is the same as the value of the datafield dict with key 8,
	                    # then the information of info_dict fits the subject of datafield_dict
	                    if v == datafield_dict['8']:
	                        if 'a' in datafield_dict: subject['subject_auto_name'] = '; '.join(datafield_dict['a'])
	                        if '0' in datafield_dict: subject['subject_auto_id'] = datafield_dict['0'][0]
	                        if 'c' in info_dict: subject['subject_auto_conf'] = '; '.join(info_dict['c'])
	                        if 'd' in info_dict: subject['subject_auto_crea'] = '; '.join(info_dict['d'])
	            if subject: subject_auto.append(subject)
	        
	        # int_subject
	        except KeyError:
	            subject = {}
	            if 'a' in datafield_dict: subject['subject_int_name'] = '; '.join(datafield_dict['a'])
	            if '0' in datafield_dict: subject['subject_int_id'] = datafield_dict['0'][0]
	            if subject: subject_int.append(subject)
    
    # remove duplicates
    if subject_auto: subject_auto = [dict(t) for t in {tuple(d.items()) for d in subject_auto}]
    if subject_int: subject_int = [dict(t) for t in {tuple(d.items()) for d in subject_int}]

    return(subject_auto, subject_int)

# -------------------------------------------- #

def transform_subject_pub(subject_pub_list):
    regexed_subjects = []
    for subject in subject_pub_list:
        regexed_subject = re.sub('^\(VLB\-\w\w\)', '', subject)
        regexed_subjects.append(regexed_subject)
    return(regexed_subjects)

# -------------------------------------------- #

def transform_ddc_notation(ddc_notation_datafields):

    def add_ddc(datafields, regex):
        ddc_dict_list = []
        if datafields: 
            for datafield_dict in datafields:
                
                # iterating over the value-lists with the key 'a'
                for value in datafield_dict['a']:
                    ddc_dict = {}
                    match = re.findall(regex, value)
                    if match: 
                        ddc_dict['ddc_notation'] = '; '.join(match)
                        for value in datafield_dict['2']: ddc_dict['ddc_provenance'] = value
                        ddc_dict_list.append(ddc_dict)
        
        # remove duplicates
        ddc_dict_list = [dict(t) for t in {tuple(d.items()) for d in ddc_dict_list}]
        
        return(ddc_dict_list)
    
    # more information: https://www.dnb.de/EN/Professionell/DDC-Deutsch/DDCinDNB/ddcindnb_node.html
    # subject categories have 2 or 3 digits e.g. 300
    ddc_subject_category = add_ddc(ddc_notation_datafields, '^\d{2,3}$')
    # short numbers have 3 digits, followed by a period and another digit e.g. 303.6
    ddc_short_number = add_ddc(ddc_notation_datafields, '^\d\d\d\.\d$')
    # full numbers have 3 digits, followed by a period and two or more digits e.g. 303.6252970956
    ddc_full_number = add_ddc(ddc_notation_datafields, '\d\d\d\.\d\d+')

    return(ddc_subject_category, ddc_short_number, ddc_full_number)

