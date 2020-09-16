# transforming.py

# fields that are not transformed at the moment: dnb_id, contenttype, edition, extent, isbn, issn, lang, series, notes

import re

# ------------------------------------------------------------------------------------------- #

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
# if there is more than one title remainder they should be already separated by ' ; '
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
            #print(datafield_dict['a'])
            imprint = {}
            if 'a' in datafield_dict: imprint['publication_place'] = '; '.join(datafield_dict['a'])
            if 'b' in datafield_dict: imprint['publisher'] = '; '.join(datafield_dict['b'])
            if 'c' in datafield_dict: imprint['publication_date'] = '; '.join(datafield_dict['c'])

            if ('publication_place' in imprint.keys()) and ('publisher' in imprint.keys()) and ('publication_date' in imprint.keys()):
                imprints.append(imprint['publication_place'] + ': ' + imprint['publisher'] + ', ' + imprint['publication_date'])

    return(imprints)

# -------------------------------------------- #

# returns the separated subjects (subject_auto, subject_partially_auto, subject_int, subject_culturegraph, subject_not_sorted, subject_maybe_int) as lists of dicts
# each subject term is in a dict with the preferred name and the id
# in case of the subject terms with an provenance info dict there is also the date when the subject term was assigned and the confidence value if it's a automatic subject

def transform_subject_lib(subject_lib_datafields, subject_info_datafields):
    def transform_single_subject_dict(subject, datafield_dict, info_dict):
        if 'a' in datafield_dict: subject['subject_pref'] = '; '.join(datafield_dict['a'])
        if '0' in datafield_dict: subject['subject_id'] = datafield_dict['0'][0]
        if 'c' in info_dict: subject['subject_conf'] = '; '.join(info_dict['c'])
        if 'd' in info_dict: subject['subject_crea'] = '; '.join(info_dict['d'])
        if 'a' in info_dict: subject['subject_generation_process'] = '; '.join(info_dict['a'])

    subject_auto = []
    subject_partially_auto = []
    subject_int = []
    subject_maybe_int = []
    subject_culturegraph = []
    subject_not_sorted = []


    if subject_lib_datafields:
        for datafield_dict in subject_lib_datafields:
            
            try:
                datafield_dict['8']
                subject = {}
                for info_dict in subject_info_datafields: 
                    for k, v in info_dict.items():
                        # if the value of info_dict is the same as the value of the datafield dict with key 8,
                        # then the information of info_dict fits the subject of datafield_dict

                        if v == datafield_dict['8']:
                            ind1 = str(' '.join(info_dict['ind1']))
                            code_a = str(' '.join(info_dict['a']))
                            if ind1 == '0':
                                transform_single_subject_dict(subject, datafield_dict, info_dict)
                                if subject: subject_auto.append(subject)
                                #print('maschinell:', subject, '\n')

                            elif ind1 == '1':
                                transform_single_subject_dict(subject, datafield_dict, info_dict)
                                if subject: subject_partially_auto.append(subject)
                                #print('teilweise maschinell:', subject, '\n')

                            elif ind1 == '2':
                                transform_single_subject_dict(subject, datafield_dict, info_dict)
                                if subject: subject_int.append(subject)
                                #print('intellektuell:', subject, '\n')
                            
                            elif code_a == 'cgwrk':
                                transform_single_subject_dict(subject, datafield_dict, info_dict)
                                if subject: subject_culturegraph.append(subject)
                                #print('culturegraph:', subject, '\n')

                            # old codes should be removed completely by 2021
                            elif code_a == 'maschinell':
                                transform_single_subject_dict(subject, datafield_dict, info_dict)
                                if subject: subject_auto.append(subject)
                            
                            else:
                                transform_single_subject_dict(subject, datafield_dict, info_dict)
                                if subject: subject_not_sorted.append(subject)
                                #print('not sorted:', subject, '\n')        
            
            # no preovenance data for the subject, should be an intellectual subject most of the time (?)
            except KeyError:
                subject = {}
                if 'a' in datafield_dict: subject['subject_pref'] = '; '.join(datafield_dict['a'])
                if '0' in datafield_dict: subject['subject_id'] = datafield_dict['0'][0]
                if subject: subject_maybe_int.append(subject)
                #print('not_sorted:', subject, '\n')
    
    # if there are automatic subjects it should be save to assume that the fields without provenance are int subjects (?)
    if subject_auto: subject_int += subject_maybe_int
    #else: subject_not_sorted += subject_maybe_int -> to change with next data release (?)

    # remove duplicates
    if subject_auto: subject_auto = [dict(t) for t in {tuple(d.items()) for d in subject_auto}]
    if subject_partially_auto: subject_partially_auto = [dict(t) for t in {tuple(d.items()) for d in subject_partially_auto}]
    if subject_int: subject_int = [dict(t) for t in {tuple(d.items()) for d in subject_int}]
    if subject_culturegraph: subject_culturegraph = [dict(t) for t in {tuple(d.items()) for d in subject_culturegraph}]
    if subject_not_sorted: subject_not_sorted = [dict(t) for t in {tuple(d.items()) for d in subject_not_sorted}]
    if subject_maybe_int: subject_maybe_int = [dict(t) for t in {tuple(d.items()) for d in subject_maybe_int}]

    return(subject_auto, subject_partially_auto, subject_int, subject_culturegraph, subject_not_sorted, subject_maybe_int)

# -------------------------------------------- #

# returns the vlb subects without the VLB prefix as list of strings

def transform_subject_vlb(subject_vlb_list):
    regexed_subjects = []
    for subject in subject_vlb_list:
        regexed_subject = re.sub('^\(VLB\-\w\w\)', '', subject)
        regexed_subjects.append(regexed_subject)
    return(regexed_subjects)

# -------------------------------------------- #

# return the ddc_notations separated into subject categories, short numbers and full numbers
# they are structured as list of dicts
# beside the number, the provenance is added to a ddc-dict 

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