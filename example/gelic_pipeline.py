# importing all needed libs
import bs4, os, requests, json, datetime, gzip, re
from gelic_mt import downloading, filtering, decoding, transforming, encoding
from lxml import etree
from zipfile import ZipFile

start = datetime.datetime.now()

# ---------------------------------------------------------------------------------------------- #

data_path = 'data/'
downloaded_path = data_path + 'downloaded/'
tmp_path = data_path + 'tmp/'
filtered_path = data_path + 'filtered/'

unzipped_corpus_v1 = 'corpus_v1.xml' 
zipped_corpus_v1 = unzipped_corpus_v1 + '.zip' # please save this file in data_path!

wanted_format = '.mrc.xml.gz'

url_to_files = 'https://data.dnb.de/DNB/'

transformed_file = data_path + 'corpus_v2.json'

# ---------------------------------------------------------------------------------------------- #

# create target directory if it doesn't exist
try:
    os.makedirs(downloaded_path)
    print('created' , downloaded_path)
except FileExistsError: print(downloaded_path, 'already exists')

# DOWNLOADING #

# get the resource of the dnb website
dnb_data_resource = requests.get(url_to_files)
dnb_soup = bs4.BeautifulSoup(dnb_data_resource.content, 'html.parser')

checksum_dict = {}
files = []

for x in dnb_soup.select('pre a'):
    file_to_download = x.attrs.get('href')
    
    if file_to_download.__contains__('Checksum') == True:
        downloading.download(url_to_files, file_to_download, downloaded_path)
        checksum_dict = downloading.create_checksum_dict(downloaded_path, file_to_download)
    elif file_to_download.__contains__(wanted_format) == True: files.append(file_to_download)

# only download the marcxmls if the checksum_dict exists, otherwise the hash can't be checked
if checksum_dict:
    for file in files:
        downloading.download(url_to_files, file, downloaded_path)
        downloading.checkhash(downloaded_path, file, checksum_dict)


# FILTERING #

# the files are filtered and saved separatly so that if something goes wrong with one file, one doesn't have to process all files again

with ZipFile(data_path + zipped_corpus_v1, 'r') as to_unzip:
    # extract to_unzip to temp/
    to_unzip.extractall(tmp_path)

wanted_ids = filtering.get_id_list(tmp_path + unzipped_corpus_v1)
print('id_list was created')
# remove unzipped corpus_v1
os.system('rm -rf ' + tmp_path + '*')

try:
    os.makedirs(filtered_path)
    print('created' , filtered_path)
except FileExistsError: print(filtered_path, 'already exists')

for infile in os.listdir(downloaded_path):
    if infile.endswith(wanted_format):

        print('filtering ' + infile + ' ...')

        # unzip the MARCXML
        unzipped_file =  infile.split('.')[0] + '.xml'
        os.system('gzip -dc < ' + downloaded_path + infile  +' > ' + tmp_path + unzipped_file)

        outputfile = filtered_path + infile.split('.')[0] + '_filtered.xml'
        os.system('touch ' + outputfile)

        # to count how many files were matched
        counter = 0

        # default way to open a xml-file when using lxml
        with etree.xmlfile(outputfile, encoding='utf-8') as out:
            out.write_declaration()
            # enclose records to be written out in collection-tag
            with out.element('collection'):
                # streaming the records
                for event, record in etree.iterparse(tmp_path + unzipped_file, tag='{http://www.loc.gov/MARC21/slim}record'):
                    
                    # removing leading zeros, otherwise the ids can't be matched
                    dnb_id = re.sub('^0', '', ''.join(decoding.get_id(record)))
                    
                    if dnb_id in wanted_ids:

                        notations = decoding.get_ddc_notation(record)

                        # filtering ddcs + checking if the record has subjects = was content-based indexed
                        not_wanted_ddcs = ['B', 'K'] # B = Belletristik -> fiction, K = Kinder- und Jugendliteratur -> children's and youth literature (YA etc.)

                        if (filtering.bool_match(notations, not_wanted_ddcs) == False) and (filtering.check_if_subject(record) == True): 
                            out.write(record)
                            counter += 1
                            print(str(counter) + '. successfull match:', dnb_id)
                        else: continue 
                        
                    record.clear()
                    # delete elements that don't have the tag '{http://www.loc.gov/MARC21/slim}record' otherwise the memory blows up 
                    # (https://stackoverflow.com/questions/16482382/lxml-and-fast-iter-eating-all-the-memory)
                    while record.getprevious() is not None: del record.getparent()[0]
        print(counter, 'matches in', infile)
        
        # empty tmp/
        os.system('rm -rf ' + tmp_path + '*')

        print('filtered ' + infile)

    else: continue


# DECODING, TRANSFORMING, ENCODING #

processing_counter = 0
with open(transformed_file, 'w') as f:
    f.write('[')  # begin a JSON array

    for infile in os.listdir(filtered_path):
        if infile.endswith('.xml'):

            print('processing ' + infile + ' ...')

            try:
                for event, record in etree.iterparse(filtered_path + infile, tag='{http://www.loc.gov/MARC21/slim}record'):
                    
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
                    subject_lib_datafields, subject_info_datafields = decoding.get_subject_lib(record)
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
                    subject_auto, subject_partially_auto, subject_int, subject_culturegraph, subject_not_sorted, subject_maybe_int = transforming.transform_subject_lib(subject_lib_datafields, subject_info_datafields)
                    subject_vlb = transforming.transform_subject_vlb(subject_vlb_list)
                    ddc_subject_category, ddc_short_number, ddc_full_number = transforming.transform_ddc_notation(ddc_notation_datafields)


                    # ENCODING #
                    transformed_record = {'collection_s' : 'dnb'}
                    if dnb_id: transformed_record['id'] = encoding.encode(dnb_id)
                    if contenttype: transformed_record['contenttype_ss'] = encoding.encode(contenttype)
                    if author: transformed_record['author_ss'] = encoding.encode(author)
                    if editor: transformed_record['editor_ss'] = encoding.encode(editor)
                    if title: transformed_record['title_txt_de'] = encoding.encode(title)
                    if edition: transformed_record['edition_ss'] = encoding.encode(edition)
                    if imprint: transformed_record['imprint_ss'] = encoding.encode(imprint)
                    if extent: transformed_record['extent_ss'] = encoding.encode(extent)
                    if isbn: transformed_record['isbn_ss'] = encoding.encode(isbn)
                    if issn: transformed_record['issn_ss'] = encoding.encode(issn)
                    if lang: transformed_record['lang_ss'] = encoding.encode(lang)
                    if series: transformed_record['series_ss'] = encoding.encode(series)
                    if notes: transformed_record['notes_ss'] = encoding.encode(notes)
                    if subject_auto: transformed_record['subject_auto_txt_de'] = encoding.encode(subject_auto)
                    if subject_partially_auto: transformed_record['subject_partially_auto_txt_de'] = encoding.encode(subject_partially_auto)
                    if subject_int: transformed_record['subject_int_txt_de'] = encoding.encode(subject_int)
                    if subject_culturegraph: transformed_record['subject_culturegraph_txt_de'] = encoding.encode(subject_culturegraph)
                    if subject_not_sorted: transformed_record['subject_not_sorted_txt_de'] = encoding.encode(subject_not_sorted)
                    if subject_maybe_int: transformed_record['subject_maybe_int_txt_de'] = encoding.encode(subject_maybe_int)
                    if subject_vlb: transformed_record['subject_vlb_txt_de'] = encoding.encode(subject_vlb)
                    if ddc_subject_category: transformed_record['ddc_subject_category_ss'] = encoding.encode(ddc_subject_category)
                    if ddc_short_number: transformed_record['ddc_short_number_ss'] = encoding.encode(ddc_short_number)
                    if ddc_full_number: transformed_record['ddc_full_number_ss'] = encoding.encode(ddc_full_number)
                    
                    # JSON encode each element and write it to the file
                    json.dump(transformed_record, f, ensure_ascii=False, indent=4) 
                    
                    # close the element entry with a comma and a new line
                    f.write(",\n") 
                    
                    record.clear()
                    
                    # again: delete elements that don't have the tag '{http://www.loc.gov/MARC21/slim}record' otherwise the memory blows up 
                    while record.getprevious() is not None: del record.getparent()[0]

                    processing_counter += 1
                    print(str(processing_counter) + '. record (' + str(dnb_id) + ') was processed')

            except etree.XMLSyntaxError: continue # if a filtered xml is empty

            print('processed ' + infile)
        
        else: continue

    f.seek(0, os.SEEK_END) # to the end of the file
    f.seek(f.tell() - 2, os.SEEK_SET) # go backwards 2 bytes
    f.write("]") # end the JSON array
    f.truncate() # remove the rest

end = datetime.datetime.now()

print('start:', start)
print('end:', end)