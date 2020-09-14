# test_transform.py

from lxml import etree
import json, re, os
from gelic_mt import decoding, transforming, encoding

infile = "data/test_corpus.xml"
#infile = "data/test_dnb_all_dnbmarc_20200213-1.mrc.xml"

with open("data/test_transformed_corpus.json", "w") as f:  # open our file for writing
    f.write("[")  # begin a JSON array
    for event, record in etree.iterparse(infile, tag="{http://www.loc.gov/MARC21/slim}record"):
        # decoding
        dnb_id = decoding.get_id(record)
        contenttype_list = decoding.get_contenttype(record)
        author_datafields = decoding.get_author(record)
        editor_datafields = decoding.get_editor(record)
        title_main, title_remainder = decoding.get_title(record)
        edition = decoding.get_edition(record)
        imprint_datafields = decoding.get_imprint(record)
        extent = decoding.get_extent(record)
        isbn = decoding.get_isbn(record)
        issn = decoding.get_issn(record)
        lang = decoding.get_lang(record)
        series_list = decoding.get_series(record)
        notes = decoding.get_notes(record)
        subject_lib_datafields, subject_auto_info_datafields = decoding.get_subject_lib(record)
        subject_vlb_list = decoding.get_subject_vlb(record)
        ddc_notation_datafields = decoding.get_ddc_notation(record)
        

        # transforming
        # (dnb_id)
        contenttype = transforming.transform_to_string(contenttype_list)
        author = transforming.transform_person(author_datafields, role = 'author')
        editor = transforming.transform_person(editor_datafields, role = 'editor')
        title = transforming.transform_title(title_main, title_remainder)
        # (edition)
        imprint = transforming.transform_imprint(imprint_datafields)
        extent = transforming.transform_to_string(extent)
        # (isbn)
        # (issn)
        # (lang)
        series = transforming.transform_to_string(series_list)
        # (notes)
        subject_auto, subject_int = transforming.transform_subject_lib(subject_lib_datafields, subject_auto_info_datafields)
        subject_vlb = transforming.transform_subject_vlb(subject_vlb_list)
        ddc_subject_category, ddc_short_number, ddc_full_number = transforming.transform_ddc_notation(ddc_notation_datafields)




        # encoding
        transformed_record = {'collection' : 'dnb'}
        if dnb_id: transformed_record['id'] = encoding.encode(dnb_id)
        if contenttype: transformed_record['contenttype'] = encoding.encode(contenttype)
        if author: transformed_record['author'] = encoding.encode(author)
        if editor: transformed_record['editor'] = encoding.encode(editor)
        if title: transformed_record['title'] = encoding.encode(title)
        if edition: transformed_record['edition'] = encoding.encode(edition)
        if imprint: transformed_record['imprint'] = encoding.encode(imprint)
        if extent: transformed_record['extent'] = encoding.encode(extent)
        if isbn: transformed_record['isbn'] = encoding.encode(isbn)
        if issn: transformed_record['issn'] = encoding.encode(issn)
        if lang: transformed_record['lang'] = encoding.encode(lang)
        if series: transformed_record['series'] = encoding.encode(series)
        if notes: transformed_record['notes'] = encoding.encode(notes)
        if subject_auto: transformed_record['subject_auto'] = encoding.encode(subject_auto)
        if subject_int: transformed_record['subject_int'] = encoding.encode(subject_int)
        if subject_vlb: transformed_record['subject_vlb'] = encoding.encode(subject_vlb)
        if ddc_subject_category: transformed_record['ddc_subject_category'] = encoding.encode(ddc_subject_category)
        if ddc_short_number: transformed_record['ddc_short_number'] = encoding.encode(ddc_short_number)
        if ddc_full_number: transformed_record['ddc_full_number'] = encoding.encode(ddc_full_number)
    

        #print(transformed_record)
        #print(json.dumps(transformed_record, ensure_ascii=False, indent=4))
        #print(json.dumps(transformed_record, indent=4))

        # JSON encode each element and write it to the file
        json.dump(transformed_record, f, ensure_ascii=False, indent=4) # problems with [Artikel 
        #json.dump(transformed_record, f, indent=4)
        
        f.write(",\n") # close the element entry with a comma and a new line
        
        record.clear()
        
        # delete elements that have not the tag "{http://www.loc.gov/MARC21/slim}record"
        # otherwise the memory blows up (https://stackoverflow.com/questions/16482382/lxml-and-fast-iter-eating-all-the-memory)
        while record.getprevious() is not None:
            del record.getparent()[0]
    
    f.seek(0, os.SEEK_END) # to the end of the file
    f.seek(f.tell() - 2, os.SEEK_SET) # go backwards 2 bytes
    f.write("]")  # end the JSON array
    f.truncate()  # remove the rest