# test_filter_no_fiction_but_subject.py

from lxml import etree
from gelmt import filtering, decoding

infile = "data/test_input.xml"
#infile = "data/test_corpus.xml"
outputfile = "data/test_filtered.xml"
#outputfile = "data/test_filtered_corpus.xml"

counter = 0
# default way to open a xml-file when using lxml
with etree.xmlfile(outputfile, encoding='utf-8') as out:
    out.write_declaration()
    # enclose records to be written out in collection-tag
    with out.element('collection'):
        # streaming the records
        for event, record in etree.iterparse(infile, tag="{http://www.loc.gov/MARC21/slim}record"):
            
            notations = decoding.get_subfields(record, '082', 'a')
            notations += decoding.get_subfields(record, '083', 'a')
            notations += decoding.get_subfields(record, '084', 'a')

            # filtering dnb_classes + ckecking if the record has subjects = was content-based indexed
            not_wanted_dnb_classes = ['B', 'K', 'S'] # B = Belletristik -> fiction, K = Kinder- und Jugendliteratur -> children's and youth literature (YA etc.), S = Schulbücher -> school textbooks

            if (filtering.bool_match(notations, not_wanted_dnb_classes) == False) and (filtering.check_if_subject(record) == True): 
                out.write(record)
                print(decoding.get_id(record), 'was saved')
                counter += 1
            else:
                print('false')



            record.clear()
            while record.getprevious() is not None:
                del record.getparent()[0]

print(counter)