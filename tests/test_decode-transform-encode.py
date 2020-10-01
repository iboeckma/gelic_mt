# test_transform.py

import json, re, os, datetime
from lxml import etree
from zipfile import ZipFile
from gelic_mt import decoding, transforming, encoding

start = datetime.datetime.now()

data_path = 'data/'
tmp_path = data_path + 'tmp/'

zipped_infile = 'test_input.xml.zip'
unzipped_infile = 'test_input.xml'

outputfile = 'test_transformed.json'

with ZipFile(data_path + zipped_infile, 'r') as to_unzip:
    # extract to_unzip to temp/
    to_unzip.extractall(tmp_path)

processing_counter = 0
with open(data_path + outputfile, "w") as f:
    f.write("[")  # begin a JSON array
    for event, record in etree.iterparse(tmp_path + unzipped_infile, tag="{http://www.loc.gov/MARC21/slim}record"):
        
        # DECODING #
        dnb_id = decoding.get_id(record)
        contenttype = decoding.get_contenttype(record)
        author_datafields = decoding.get_author(record)
        editor_datafields = decoding.get_editor(record)
        title_main, title_remainder = decoding.get_title(record)
        edition = decoding.get_edition(record)
        imprint_datafields = decoding.get_imprint(record)
        extent = decoding.get_extent(record)
        isbn = decoding.get_isbn(record)
        issn = decoding.get_issn(record)
        lang = decoding.get_lang(record)
        series = decoding.get_series(record)
        notes = decoding.get_notes(record)
        subject_lib_datafields, subject_provenance_datafields = decoding.get_subject_lib(record)
        subject_vlb_list = decoding.get_subject_vlb(record)
        ddc_notation_datafields = decoding.get_ddc_notation(record)
        

        # TRANSFORMING #
        # (dnb_id)
        # (contenttype)
        author = transforming.transform_person(author_datafields, role = 'author')
        editor = transforming.transform_person(editor_datafields, role = 'editor')
        title = transforming.transform_title(title_main, title_remainder)
        # (edition)
        imprint = transforming.transform_imprint(imprint_datafields)
        # (extent)
        # (isbn)
        # (issn)
        # (lang)
        # (series)
        # (notes)
        subject_auto, subject_int, subject_other = transforming.transform_subject_lib(subject_lib_datafields, subject_provenance_datafields)
        subject_vlb = transforming.transform_subject_vlb(subject_vlb_list)
        ddc = transforming.transform_ddc_notation(ddc_notation_datafields)


        # ENCODING #
        transformed_record = {'collection_s' : 'dnb'}
        if dnb_id: transformed_record['id'] = encoding.json_encode(dnb_id)
        if contenttype: transformed_record['contenttype_ss'] = encoding.json_encode(contenttype)
        if author: transformed_record['author_ss'] = encoding.json_encode(author)
        if editor: transformed_record['editor_ss'] = encoding.json_encode(editor)
        if title: transformed_record['title_txt_de'] = encoding.json_encode(title)
        if edition: transformed_record['edition_ss'] = encoding.json_encode(edition)
        if imprint: transformed_record['imprint_ss'] = encoding.json_encode(imprint)
        if extent: transformed_record['extent_ss'] = encoding.json_encode(extent)
        if isbn: transformed_record['isbn_ss'] = encoding.json_encode(isbn)
        if issn: transformed_record['issn_ss'] = encoding.json_encode(issn)
        if lang: transformed_record['lang_ss'] = encoding.json_encode(lang)
        if series: transformed_record['series_ss'] = encoding.json_encode(series)
        if notes: transformed_record['notes_ss'] = encoding.json_encode(notes)
        if subject_auto: transformed_record['subject_auto_txt_de'] = encoding.json_encode(subject_auto)
        if subject_int: transformed_record['subject_int_txt_de'] = encoding.json_encode(subject_int)
        if subject_other: transformed_record['subject_other_txt_de'] = encoding.json_encode(subject_other)
        if subject_vlb: transformed_record['subject_vlb_txt_de'] = encoding.json_encode(subject_vlb)
        if ddc: transformed_record['ddc_ss'] = encoding.json_encode(ddc)

        # JSON encode each element and write it to the file
        json.dump(transformed_record, f, ensure_ascii=False, indent=4)
        
        # close the element entry with a comma and a new line
        f.write(",\n") 
        
        record.clear()
        
        # delete elements that have not the tag "{http://www.loc.gov/MARC21/slim}record" otherwise the memory blows up 
        while record.getprevious() is not None: del record.getparent()[0]
        
        processing_counter += 1
        print(str(processing_counter) + '. record (' + str(dnb_id) + ') was processed')
    
    f.seek(0, os.SEEK_END) # to the end of the file
    f.seek(f.tell() - 2, os.SEEK_SET) # go backwards 2 bytes
    f.write("]")  # end the JSON array
    f.truncate()  # remove the rest

os.system('rm -rf ' + tmp_path + '*')

print('saved to', outputfile)

end = datetime.datetime.now()

print('start:', start)
print('end:', end)