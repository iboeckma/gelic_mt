# importing all needed libs
import bs4, os, requests
from gelic_mt import downloading

# declare wanted target directory
dir_path = "data/downloaded/"

# declare wanted file format ("has to contain")
wanted_format = '.mrc.xml.gz'

url_to_files = 'https://data.dnb.de/DNB/'

# create target directory if it doesn't exist
try:
    os.makedirs(dir_path)
    print("created " , dir_path)
except FileExistsError:
    print(dir_path + " already exists")

# download the files
dnb_data_resource = requests.get(url_to_files)
dnb_soup = bs4.BeautifulSoup(dnb_data_resource.content, "html.parser")

checksum_dict = {}
files = []
for x in dnb_soup.select('pre a'):
    file_to_download = x.attrs.get('href')
    
    if file_to_download.__contains__('Checksum') == True:
        downloading.download(url_to_files, file_to_download, dir_path)
        checksum_dict = downloading.create_checksum_dict(dir_path, file_to_download)
    elif file_to_download.__contains__(wanted_format) == True:
        files.append(file_to_download)

# only download the marcxmls if the checksum_dict exist, otherwise the hash can't be checked
if checksum_dict:
    for file in files:
        downloading.download(url_to_files, file, dir_path)
        downloading.checkhash(dir_path, file, checksum_dict)