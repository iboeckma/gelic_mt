# German Library MARCXML Tools (GeLMT)
GeLMT provides modules that help with _filtering_, _decoding_, _transforming_ and _encoding_ __MARCXML__ data of the __German National Library (DNB)__. The modules are relying on the library __[lxml](https://lxml.de/)__. The package was designed for building a pipeline for the project __[German Library Indexing Collection (GeLIC)](https://github.com/irgroup/gelic)__. For example a specific need of this collection is to preserve the difference between automatically indexed (machine) and intellectually indexed (librarian) subject terms.

## Downloading
Basic methods that scrape the MARCXML files of the [dnb website](https://data.dnb.de/DNB/), compare the checksum, ...

## Filtering
There are three methods which can be helpful for filtering the data.
1. `check_if_subject(record)` - returns `True` if a record was already subject indexed by a librarian or machine
2. `bool_match(values_to_match_with, values_to_match_on)` - compare two lists, if one value matches return `True`; which can be useful for filtering out specific subject categories like `B` for fiction
3. `get_id_list` - is a method for creating a list of all ids of the old corpus of GeLIC to search the new data with these ids

## Decoding
Three main methods provide access to the different levels of a MARCXML: <br/> 
__get_controlfields()__, __get_datafields()__ and __get_subfields()__

Methods like `get_author()` use these functions with the specific rules for them, e.g. for author: When there is no field `100`, look for editors in field `700`. If no editor is found, look for an organisation in field `110`. The other methods are: `get_id()`, `get_contenttype()`, `get_editor()`, `get_title()`, `get_edition()`, `get_imprint()`, `get_extent()`, `get_isbn()`, `get_issn`, `get_lang()`, `get_series()`, `get_notes()`, `get_lib_subject()`, `get_pub_subject()` and `get_ddc_notation()`

### controlfields
```xml
<?xml version="1.0" encoding="UTF-8"?>
  <record xmlns="http://www.loc.gov/MARC21/slim" type="Bibliographic">
    <controlfield tag="001">1200497457</controlfield> 
      
      ...
    
  </record>
```
__`get_controlfield(record, '001')`__ -> returns the value of the first controlfield with the wanted tag as string: `'1200497457'`

### datafields
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
__`get_datafields(record, '700')`__ -> returns a list of dicts; every dictionary is a representation of a field with the tag `700`:
```
[{
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
   'a' : ['Hering, Hendrik'],
   'e' : ['Herausgeber'],
   '4' : ['edt']
  }]
```

### subfields
__`get_subfields(record, '700, 'a')`__ -> returns all values of all subfields with the code `a` of the datafields with the tag `700`: `['Glaab, Manuela', 'Hering, Hendrik']`

## Transforming
- at the moment there are seven methods for transforming the data
- IDs with the prefix (DE-588) are the preferred choice when choosing an id out of a list

methods: `transform_to_string()`, `transform_person()`, `transform_title()`, `transform_imprint()`, `transform_lib_subject()`, `transform_subject_pub()`, `transform_ddc_notation()`

### example: transform_person()
returns a list of dicts: a dict contains the name of the person and an id if possible

`transform_person(person_datafields, role = 'editor')` <br/> 
-> `[{ 'editor_name' : 'Glaab, Manuela', 'editor_id' : '(DE-588)113094744'}, {'editor_name' : 'Hering, Hendrik'}]`

### example: transform_ddc_notation()
- returns the lists of dictionaries: ddc_subject_category, ddc_short_number, ddc_full_number
- the values are assigned by using regex to one of the lists

`transform_ddc_notation(ddc_notation_datafields)` <br/> 
-> `ddc_subject_category` = `[{'ddc_notation' : '550', 'ddc_provenance' : '22sdnb'},{'ddc_notation' : '796', 'ddc_provenance' : '22sdnb'}]` <br/> 
-> `ddc_full_number` = `[{'ddc_notation' : '551.57848', 'ddc_provenance' : '22/ger'}]`
 
## Encoding
pass a value: str / list of strings / list of dicts
- string or a list of strings: return the passed value
- list of dicts: return a list of strings -> each string contains the values of a dict, separated by ' -- '

(also, every string that is returned is transformed from nfd to nfc)

`encode(editors)` -> `['Glaab, Manuela -- (DE-588)113094744', 'Hering, Hendrik']`
