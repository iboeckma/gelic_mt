# test_filter_by_record_id.py

import re, os, datetime
from lxml import etree
from zipfile import ZipFile
from gelic_mt import filtering, decoding

start = datetime.datetime.now()

data_path = 'data/'
tmp_path = data_path + 'tmp/'

zipped_ids_to_extract = 'test_ids-to-extract.xml.zip'
unzipped_ids_to_extract = 'test_ids-to-extract.xml'

zipped_infile = 'test_input.xml.zip'
unzipped_infile = 'test_input.xml'

outputfile = 'test_filtered-by-id.xml'

# EXTRACTING THE IDs
with ZipFile(data_path + zipped_ids_to_extract, 'r') as to_unzip:
    # extract to_unzip to temp/
    to_unzip.extractall(tmp_path)

wanted_ids = filtering.get_id_list(tmp_path + unzipped_ids_to_extract)
print('id_list was created')

os.system('rm -rf ' + tmp_path + '*')


with ZipFile(data_path + zipped_infile, 'r') as to_unzip:
    # extract to_unzip to temp/
    to_unzip.extractall(tmp_path)

counter = 0
# default way to open a xml-file when using lxml
with etree.xmlfile(data_path + outputfile, encoding='utf-8') as out:
    out.write_declaration()
    # enclose records to be written out in collection-tag
    with out.element('collection'):
        # streaming the records
        for event, record in etree.iterparse(tmp_path + unzipped_infile, tag="{http://www.loc.gov/MARC21/slim}record"):
            
            dnb_id = re.sub('^0', '', ''.join(decoding.get_id(record)))
            
            # MATCHING
            if dnb_id in wanted_ids:
                out.write(record)
                counter += 1
                print('successfull match:', dnb_id)
            else:
                print('not a match:', dnb_id)
            
            # delete elements that don't have the tag '{http://www.loc.gov/MARC21/slim}record' otherwise the memory blows up 
            record.clear()
            while record.getprevious() is not None:
                del record.getparent()[0]

print(counter, 'matches in', unzipped_infile)

os.system('rm -rf ' + tmp_path + '*')

print('saved to', outputfile)

end = datetime.datetime.now()

print('start:', start)
print('end:', end)