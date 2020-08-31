# downloading.py

# importing all needed libs
import requests, hashlib, sys
from pathlib import Path

def create_checksum_dict(dir_path, checksum_file):
    checksum_dict = {}
    with open(dir_path + checksum_file, 'r') as infile:
        # skip first line
        next(infile)
        for line in infile:
            # condense multiple whitespaces to one
            condensed_whitespaces = ' '.join(line.split())
            splitted_line = condensed_whitespaces.split(' ')
            # add file and checksum as key and value to checksum_dict
            checksum_dict[splitted_line[0]] = splitted_line[1]
    
    print('created checksum_dict')
    return checksum_dict

def checkhash(filepath, file, checksum_dict):
    
    if checksum_dict:
        sha256_hash = hashlib.sha256()
        with open(filepath + "/" + file,"rb") as f:
            # "read and update hash string value in blocks of 4K"
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
            calculated_hash = sha256_hash.hexdigest()
        # get the hash out of the dictionary, can use 'file' as key
        dnb_hash = checksum_dict.get(file)
        if calculated_hash == dnb_hash: 
            print('hash of the downloaded file and the checksum_dict match')
            return
        else:
            sys.exit("hash of the downloaded file and the checksum_dict don't match")

    else: sys.exit("create_checksum_dict before trying to checkhash a file")

def download(url, file, dir_path):
    
    filepath = Path(dir_path + file)

    # check if file exists already
    try: filepath.resolve(strict=True)
        
    except FileNotFoundError:
        url_to_download = "https://data.dnb.de/DNB/" + file
        print("trying to download " + file + " ...")
        resource = requests.get(url_to_download)

        # check if download was successful
        if resource.status_code == 404:
            sys.exit(file + " is not available for download")
            
        else:
            # write downloaded resource to file 
            open(filepath, 'wb').write(resource.content)
            
            # check if file exists again
            try: filepath.resolve(strict=True)
            except FileNotFoundError: sys.exit("could not download " + file)
            else: print("downloaded " + file)

    else: print(file + " already exists")