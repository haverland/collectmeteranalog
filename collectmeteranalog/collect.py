from urllib.error import HTTPError, URLError
import urllib.request
import re
import requests
import os
import sys
from PIL import Image
from datetime import date, timedelta
import imagehash
import secrets
import shutil
from collectmeteranalog.labeling import label
import time
import numpy as np


target_raw_path =  "data/raw_images"   # here all raw images will be stored
target_label_path = "data/labeled"
target_store_duplicates = "data/raw_images/duplicates"
target_hash_data = "data/HistoricHashData.txt"


def yesterday(daysbefore=1):
    ''' return the date of yesterday as string in format yyyymmdd'''
    yesterday = date.today() - timedelta(days=daysbefore)
    return yesterday.strftime("%Y%m%d")


def readimages(servername, output_dir, daysback=3):
    '''get all images taken within defined days back and store it in target path'''
    
    if not servername.startswith("http://"):
        serverurl = "http://" + servername
    else:
        serverurl = servername

    print(f"Download images from {serverurl} ...")
    count = 0

    for datesbefore in range(0, daysback):
        picturedate = yesterday(daysbefore=datesbefore)

        for i in range(24):
            hour = f'{i:02d}'
            
            path = os.path.join(output_dir, servername, picturedate, hour)
            if os.path.exists(path):
                continue

            try:
                print("Download images from folder: /fileserver/log/analog/" + picturedate + "/" + hour)
                url_list = f"{serverurl}/fileserver/log/analog/{picturedate}/{hour}/"
                fp = urllib.request.urlopen(url_list)
                url_list_str = fp.read().decode("utf8")
                fp.close()

            except HTTPError as h:
                print(f"{url_list} not found")
                continue
            
            except URLError as ue:
                print("URL-Error! Server not available? Requested URL was:", url_list)
                sys.exit(1)
            
            urls = re.findall(r'href=[\'"]?([^\'" >]+)', url_list_str)
            os.makedirs(path, exist_ok=True) 

            for url in urls:
                # Skip files which are not jpg
                if not url.lower().endswith(('.jpg', '.jpeg')):
                    continue

                prefix = os.path.basename(url).split('_', 1)[0]
                if (prefix == os.path.basename(url)):
                    prefix = ''
                else:
                    prefix = prefix + '_'
                
                filename = secrets.token_hex(nbytes=16) + ".jpg"
                filepath = os.path.join(path, prefix + filename)

                # Skip existing path
                if os.path.exists(filepath):
                    continue

                countrepeat = 10
                while countrepeat > 0:
                    try:
                        print(serverurl+url)
                        with requests.get(serverurl+url, stream=True, timeout=15) as response:
                            # Check for HTTP errors
                            response.raise_for_status()

                            content_type = response.headers.get("Content-Type", "")

                            if content_type == "image/jpeg":
                                # Save directly without re-encoding
                                with open(filepath, "wb") as f:
                                    for chunk in response.iter_content(chunk_size=8192):
                                        f.write(chunk)
                            else:
                                # Re-encode to JPEG
                                img = Image.open(response.raw)
                                img = img.convert("RGB")  # ensures JPEG compatibility
                                img.save(filepath, format="JPEG", quality=100)

                            count += 1
                            break
                
                    except requests.exceptions.Timeout:
                        print(filepath + " timed out - Retrying in 10 s ... | (%d)..." % (countrepeat - 1))
                        countrepeat -= 1
                        time.sleep(10)
                        continue

                    except (requests.exceptions.RequestException, OSError) as e:
                        print(filepath + f" failed to load: {e}")
                        break

                    except Exception as e:
                        print(filepath + f" unexpected error: {e}")
                        break

    print(f"{count} images downloaded from {servername}")


def save_hash_file(images, hashfilename):
    f =  open(hashfilename, 'w', encoding='utf-8')
    for hash, img, meter, datum in images:
        f.write(datum + "\t" + meter+ "\t" + img + "\t" + str(hash)+'\n');
    f.close


def load_hash_file(hashfilename):
    images = []

    try:
        file1 = open(hashfilename, 'r')
        Lines = file1.readlines()
        file1.close
    except Exception as e:
        print('No historic Hashdata could be loaded (' + hashfilename + ')')
        return images

    for line in Lines:
        cut = line.strip('\n').split(sep="\t")
        datum = cut[0]
        meter = cut[1]
        _hash = imagehash.hex_to_hash(cut[3])
        images.append([_hash, cut[2], meter, datum])
    return images


def ziffer_data_files(input_dir):
    '''return a list of all images in given input dir in all subdirectories'''
    imgfiles = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if (file.endswith(".jpg")):
                imgfiles.append(root + "/" + file)
    return  imgfiles


def remove_similar_images(path, image_filenames, meter, similarbits=2,  hashfunc = imagehash.average_hash, saveduplicates=False):
    '''removes similar images.

    '''
    images = []
    count = 0
    print(f"Find similar images now in {len(image_filenames)} images ..." )

    datum = date.today().strftime("%Y-%m-%d")

    for img in sorted(image_filenames):
        try:
            hash = hashfunc(Image.open(img).convert('L').resize((32,20)))
        except Exception as e:
            print('Problem: ', e, ' with ', img)
            continue
        images.append([hash, img, meter, datum])
  
    if (os.path.exists(os.path.join(path, target_hash_data))):
        HistoricHashData = load_hash_file(os.path.join(path, target_hash_data))
    else:
        HistoricHashData = []

    duplicates = {}
    for hash in images:
        if (hash[1] not in duplicates):
            similarimgs = [i for i in HistoricHashData if abs(i[0]-hash[0]) < similarbits and i[1]!=hash[1]]
            if len(similarimgs) > 0:               # es wurden in den alten hashes schon vergleichbare bilder gefunden
                if (duplicates == {}):
                    duplicates = {hash[1]}
                else:
                    duplicates |= {hash[1]}
            else:                                   # es wird in den neuen Biler gesucht gefunden
                similarimgs = [i for i in images if abs(i[0]-hash[0]) < similarbits and i[1]!=hash[1]]

                if len(similarimgs) > 0:  # es wurden in den den neuen images schon vergleichbare bilder gefunden

                    if (duplicates == {}):
                        duplicates = set([row[1] for row in similarimgs])
                    else:
                        duplicates |= set([row[1] for row in similarimgs])

    # extend Historic Hash Data
    for _image in images:
        if not _image[1] in duplicates:
            HistoricHashData.append(_image)
    save_hash_file(HistoricHashData, os.path.join(path, target_hash_data))
            
    # remove now all duplicates
    if saveduplicates:
        os.makedirs(os.path.join(path, target_store_duplicates), exist_ok=True)
        count = 0
        for image in duplicates:
            count = count + 1
            os.replace(image, os.path.join(os.path.join(path, target_store_duplicates), os.path.basename(image)))
        print(f"{count} duplicates will moved to .../raw_images/duplicates.")
    else:
        count = 0
        for image in duplicates:
            count = count + 1
            os.remove(image)
        print(f"{count} duplicates will be removed.")


def move_to_label(path, keepolddata, files):
    
    os.makedirs(os.path.join(path, target_label_path), exist_ok=True)
    if (keepolddata):
        print("Copy files to folder 'labeled', keep source folder 'raw_images'")
        for file in files:
                shutil.copy(file, os.path.join(os.path.join(path, target_label_path), os.path.basename(file)))
    else:
        print("Move files to folder 'labeled' and cleanup source folder 'raw_images'")
        for file in files:
            os.replace(file, os.path.join(os.path.join(path, target_label_path), os.path.basename(file)))

        shutil.rmtree(os.path.join(path, target_raw_path))


def collect(meter, path, days, keepolddata=False, download=True, startlabel=0, saveduplicates=False, ticksteps=1, similarbits=2):
    # ensure the target path exists
    os.makedirs(os.path.join(path, target_raw_path), exist_ok=True)

    # read all images from meters
    if download:
        print("Download images")
        readimages(meter, os.path.join(path, target_raw_path), days)
    
    # remove all same or similar images and remove the empty folders
    remove_similar_images(path, ziffer_data_files(os.path.join(os.path.join(path, target_raw_path), meter)), 
                          meter, saveduplicates=saveduplicates, similarbits=similarbits)

    # move or copy the files in one zip without directory structure and optional cleanup source
    move_to_label(path, keepolddata, ziffer_data_files(os.path.join(os.path.join(path, target_raw_path), meter)))

    # label images
    label(os.path.join(path, target_label_path), startlabel=startlabel, ticksteps=ticksteps)
