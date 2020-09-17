# German Library Indexing Collection MARCXML Tools
GeLIC MT provides modules that help with _downloading_, _filtering_, _decoding_, _transforming_ and _encoding_ __MARCXML__ data of the __German National Library (DNB)__. The modules are relying on the library __[lxml](https://lxml.de/)__. The package was designed for building a pipeline for the project __[German Library Indexing Collection (GeLIC)](https://github.com/irgroup/gelic)__.

A specific need of this collection is for example the seperation of __automatically indexed__ (by software) and __intellectually indexed__ (by a librarian) subject terms.

## Table of Contents
- [Get started](#get-started)
   - [Installation](#installation)
   - [Usage](#usage)
      - [Tests](#tests)
      - [Example: GeLIC](#example-gelic)
      - [Building your own Pipeline](#building-your-own-pipeline)
- [Modules](#modules)
   - [Downloading](#downloading) 
   - [Filtering](#filtering)
   - [Decoding](#decoding)
      - [High-level Methods](#high-level-methods)
      - [Controlfields](#controlfields)
      - [Datafields](#datafields)
      - [Subfields](#subfields)
   - [Transforming](#transforming)
   - [Encoding](#encoding)

## Get started
### Installation
After cloning the repository, change into it's directory:
```
git clone https://github.com/iboeckma/gelic_mt.git
cd gelic_mt
```
Then install gelic_mt and the required packages for gelic_mt:
```
pip install .
pip install -r requirements.txt
```

### Usage
#### Tests
There are a few scripts in `tests/` which are used in development but can also help to get to know the modules. After installing the package the scripts are executable in the folder `tests/`.

__`test_downloading.py`__<br />
Downloads and verifies the newest MARCXML files of https://data.dnb.de/DNB/.

__`test_filter-by-id.py`__<br />
Extracts IDs of `data/test_ids-to-extract.xml.zip` to then compare the IDs and extract the corresponding records of the file `data/test_input.xml.zip`. Results in `data/test_filtered-by-id.xml`

__`test_filter-by-ddc-and-subject.py`__<br />
Filters out fiction titles as well as records without subjects that were assigned by the DNB of `data/test_input.xml.zip`. Results in `data/test_filtered-by-ddcs-and-subject.xml`.

__`test_decode-transform-encode.py`__<br />
Decodes, transforms and encodes the records of `data/test_input.xml.zip`. Results in `data/test_transformed.json`.

#### Example: GeLIC
The current pipeline for the GeLIC testcollection can be found in `example/gelic-pipeline.py`. It's mostly a merged version of the `tests/` scripts.

#### Building your own Pipeline
For writing your own pipeline you could start with the following:

```python
from lxml import etree
from gelic_mt import decoding, transforming, encoding

infile = 'your_file.xml'

for event, record in etree.iterparse(infile, tag="{http://www.loc.gov/MARC21/slim}record"):
  # decode something of the infile
  record_id = decoding.get_id(record)
  title_main, title_remainder = decoding.get_title(record)
  
  # transform something like the title (merges the title, separated by ' : ')
  title = transforming.transform_title(title_main, title_remainder)
  
  # encode it
  transformed_record = {'collection' : 'test'}
  if record_id: transformed_record['id'] = encoding.encode(record_id)
  if title: transformed_record['title'] = encoding.encode(title)
  
  print(transformed_record)
  
  # make sure that your memory doesn't blow up
  record.clear()
  
  while record.getprevious() is not None: 
      del record.getparent()[0]
```

## Modules
### Downloading
Three basic methods that scrape the MARCXML files of the [DNB website](https://data.dnb.de/DNB/) and verify the download: 

__`download(url, file, dir_path)`__<br />
Tries to download a file if it doesn't exist in the requested directory.

__`create_checksum_dict(dir_path, checksum_file)`__<br />
Needs a file which is structured like the checksum file that the DNB provides on their website. The script creates a dictionary with the filenames as key and the corresponding sha256 hashs as values.

__`checkhash(filepath, file, checksum_dict)`__<br /> 
If a checksum dictionary was created, the files can be verified after download.

### Filtering
There are three methods which can be helpful for filtering the data.

__`check_if_subject(record)`__<br />
Returns `True` if a record was already subject indexed by a librarian or machine.

__`bool_match(values_to_match_with, values_to_match_on)`__<br />
Compare two lists, if one value matches return `True`. As an example this can be useful for filtering out specific subject categories / DDCs like `B` for fiction.

__`get_id_list(filepath)`__<br /> 
A method for extracting a list of all ids of a file. The file has to have a XML-structure like the first version of the GeLIC corpus. This file is provided in the repository of [GeLIC](https://github.com/irgroup/gelic). The list can then be used to extract the corresponding records of another file.

### Decoding
Three main methods provide access to the different levels of a MARCXML: __`get_controlfields(record, wanted_tag)`__, __`get_datafields(record, wanted_tag)`__ and __`get_subfields(record, wanted_tag, wanted_code)`__

#### High-level Methods
Methods like `get_author()` use these functions with the specific rules for them, e.g. for author: After looking for authors in field `100`, search for other authors in field `700`. If there are no authors found, look for editors in field `700` (but do not save them as authors). If no editor is found, search for an organisation in field `110` as an author. 

All methods: `get_id()`, `get_contenttype()`, `get_author()`, `get_editor()`, `get_title()`, `get_edition()`, `get_imprint()`, `get_extent()`, `get_isbn()`, `get_issn()`, `get_lang()`, `get_series()`, `get_notes()`, `get_subject_lib()`, `get_subject_vlb()` and `get_ddc_notation()`

#### controlfields
```xml
<?xml version="1.0" encoding="UTF-8"?>
  <record xmlns="http://www.loc.gov/MARC21/slim" type="Bibliographic">
    <controlfield tag="001">1200497457</controlfield> 
      
      ...
    
  </record>
```
__`get_controlfield(record, '001')`__ -> returns the value of the first controlfield with the wanted tag as string: `'1200497457'`

#### datafields
```xml
<?xml version="1.0" encoding="UTF-8"?>
  <record xmlns="http://www.loc.gov/MARC21/slim" type="Bibliographic">
    <controlfield tag="001">1200497457</controlfield> 
    
      ...
    
    <datafield tag="700" ind1="1" ind2=" ">
      <subfield code="0">(DE-588)113094744</subfield>
      <subfield code="0">https://d-nb.info/gnd/113094744</subfield>
      <subfield code="0">(DE-101)113094744</subfield>
      <subfield code="a">Glaab, Manuela</subfield>
      <subfield code="d">1967-</subfield>
      <subfield code="e">Herausgeber</subfield>
      <subfield code="4">edt</subfield>
      <subfield code="2">gnd</subfield>
    </datafield>
    
    <datafield tag="700" ind1="1" ind2=" ">
      <subfield code="a">Hering, Hendrik</subfield>
      <subfield code="e">Herausgeber</subfield>
      <subfield code="4">edt</subfield>
    </datafield>
    
      ...
    
  </record>
```
__`get_datafields(record, '700')`__ -> returns a list of dicts; every dictionary is a representation of a field with the tag `700`, indicators are also saved like the subfields:
```
[{
  'ind1' : ['1'],
  'ind2' : [''],
  '0' : ['(DE-588)113094744', 
         'https://d-nb.info/gnd/113094744', 
         '(DE-101)113094744'], 
  'a' : ['Glaab, Manuela'],
  'd' : ['1967'],
  'e' : ['Herausgeber'],
  '4' : ['edt'],
  '2' : ['gnd']
  },
  {
   'ind1' : ['1'],
   'ind2' : [''],
   'a' : ['Hering, Hendrik'],
   'e' : ['Herausgeber'],
   '4' : ['edt']
  }]
```

#### subfields
__`get_subfields(record, '700, 'a')`__ -> returns all values of all subfields with the code `a` of the datafields with the tag `700`: `['Glaab, Manuela', 'Hering, Hendrik']`

### Transforming
- at the moment there are seven methods for transforming the data
- IDs with the prefix (DE-588) are the preferred choice when choosing an id out of a list

methods: `transform_to_string()`, `transform_person()`, `transform_title()`, `transform_imprint()`, `transform_lib_subject()`, `transform_subject_pub()`, `transform_ddc_notation()`

#### example: transform_person()
returns a list of dicts: a dict contains the name of the person and an id if possible

`transform_person(person_datafields, role = 'editor')` <br/> 
-> `[{ 'editor_name' : 'Glaab, Manuela', 'editor_id' : '(DE-588)113094744'}, {'editor_name' : 'Hering, Hendrik'}]`

#### example: transform_ddc_notation()
- returns the lists of dictionaries: ddc_subject_category, ddc_short_number, ddc_full_number
- the values are assigned by using regex to one of the lists

`transform_ddc_notation(ddc_notation_datafields)` <br/> 
-> `ddc_subject_category` = `[{'ddc_notation' : '550', 'ddc_provenance' : '22sdnb'},{'ddc_notation' : '796', 'ddc_provenance' : '22sdnb'}]` <br/> 
-> `ddc_full_number` = `[{'ddc_notation' : '551.57848', 'ddc_provenance' : '22/ger'}]`
 
### Encoding
pass a value: str / list of strings / list of dicts
- string or a list of strings: return the passed value
- list of dicts: return a list of strings -> each string contains the values of a dict, separated by ' -- '

(also, every string that is returned is transformed from nfd to nfc)

`encode(editors)` -> `['Glaab, Manuela -- (DE-588)113094744', 'Hering, Hendrik']`
