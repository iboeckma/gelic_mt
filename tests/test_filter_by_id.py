# test_filter_by_record_id.py

from lxml import etree
from gelic_mt import filtering, decoding
import re

infile = "data/test_input.xml"
#infile = "data/test_corpus.xml"
outputfile = "data/test_filtered_by_id.xml"
wanted_ids = filtering.get_id_list('data/test_old_corpus.xml')
print('id_list was created')

# default way to open a xml-file when using lxml
with etree.xmlfile(outputfile, encoding='utf-8') as out:
    out.write_declaration()
    # enclose records to be written out in collection-tag
    with out.element('collection'):
        # streaming the records
        for event, record in etree.iterparse(infile, tag="{http://www.loc.gov/MARC21/slim}record"):
            
            # dnb_id = ''.join(decoding.get_id(record))
            dnb_id = re.sub('^0', '', ''.join(decoding.get_id(record)))
            
            if dnb_id in wanted_ids:
                out.write(record)
                print('successfull match:', dnb_id)
            #else:
             #   print('false')
                
            record.clear()
            while record.getprevious() is not None:
                del record.getparent()[0]