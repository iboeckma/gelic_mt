# importing all needed libs
import bs4, os, requests, datetime
from gelic_mt import downloading

start = datetime.datetime.now()

# ---------------------------------------------------------------------------------------------- #

data_path = 'data/'
downloaded_path = data_path + 'downloaded/'

wanted_format = '.mrc.xml.gz'

url_to_files = 'https://data.dnb.de/DNB/'

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

end = datetime.datetime.now()

print('start:', start)
print('end:', end)