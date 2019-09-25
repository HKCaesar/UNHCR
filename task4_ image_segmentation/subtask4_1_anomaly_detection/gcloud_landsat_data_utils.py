from google.cloud import storage
# Set up google cloud api: https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python

import datetime as dt
import requests
import zipfile
import io
import ogr
import shapely.wkt
import shapely.geometry
import os
import re
import logging
from pathlib import Path
import argparse

get_dir = lambda n : n if len(n) == 3 else '0'*(3 - len(n)%3)+n

def list_blobs_with_prefix(bucket_name: str, prefix: str, delimiter=None):
    """
    Get the list of all the object in a bucket with a given prefix
    """
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix,
                                      delimiter=delimiter)

    return blobs

def get_all_dates(path: str, row: str):    # Pass path and row as strings
    """
    Get all unique dates of images in a Path/Row
    """
    global get_dir
    prefix = 'LC08/01/{}/{}/'.format(path, row)
    path = get_dir(path)
    row = get_dir(row)
    blobs = list_blobs_with_prefix('gcp-public-data-landsat', prefix)
    dates = list(set(i.name.split('/')[-1].split('_')[3] for i in blobs))
    dates = [dt.datetime.strptime(i, '%Y%m%d') for i in dates]
    return dates

def checkPoint(feature, point, mode):
    geom = feature.GetGeometryRef()
    shape = shapely.wkt.loads(geom.ExportToWkt())
    if point.within(shape) and feature['MODE']==mode:
        return True
    else:
        return False

def get_pathrow_from_latlon(lat, lon):
    shapefile = 'landsat-path-row/WRS2_descending.shp'
    if not os.path.isfile('landsat-path-row/WRS2_descending.shp'):
        url = "https://prd-wret.s3-us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/atoms/files/WRS2_descending_0.zip"
        r = requests.get(url)
        zip_file = zipfile.ZipFile(io.BytesIO(r.content))
        zip_file.extractall("landsat-path-row")
        zip_file.close()
    wrs = ogr.Open(shapefile)
    layer = wrs.GetLayer(0)
    point = shapely.geometry.Point(lon, lat)
    mode = 'D'
    i=0
    while not checkPoint(layer.GetFeature(i), point, mode):
        i += 1
    feature = layer.GetFeature(i)
    path = feature['PATH']
    row = feature['ROW']
    return path, row

def get_blob_names(prefix, path, row, date, bands):
    global get_dir
    patterns = [re.compile("{}.*_{}{}_{}_.*_B{}\D.*".format(prefix, path, row, date, band)) for band in bands]
    path = get_dir(path)
    row = get_dir(row)
    blobs = list_blobs_with_prefix('gcp-public-data-landsat', prefix)
    blob_names = []
    for blob in blobs:
        for pattern in patterns:
            if pattern.match(blob.name):
                blob_names.extend([blob.name])
    return blob_names

def get_filename_from_blobname(blob_name):
    return blob_name.split('/')[-1]

def create_download_directory(path, row, date, download_dir):
    pathrow_dir = download_dir / Path("{}{}".format(path, row))
    if not os.path.isdir(pathrow_dir):
        os.makedirs(pathrow_dir)
        os.makedirs(pathrow_dir / date)
        logging.info('Download directories created.')
    elif not os.path.isdir(pathrow_dir / date):
        os.makedirs(pathrow_dir / date)
        logging.info('Download directories created.')
    else:
        logging.info("Download directories aready present. Skipping")
    return pathrow_dir / date

def get_bands(path, row, date: str, bands, download_dir = Path('')): # dates in "yyyymmdd" format and bands as an iterable
    global get_dir
    logging.getLogger().setLevel(logging.INFO)
    path = get_dir(path)
    row = get_dir(row)
    prefix = 'LC08/01/{}/{}/'.format(path, row)
    logging.info('Getting Blob names')
    blob_names = get_blob_names(prefix, path, row, date, bands)
    if len(blob_names) != 0:
        logging.info("Found {} blobs".format(len(blob_names)))
        logging.info('Creating download directories.')
        try:
            os.makedirs(download_dir)
        except:
            pass
        download_dir = create_download_directory(path, row, date, download_dir)
        storage_client = storage.Client()
        bucket = storage_client.get_bucket('gcp-public-data-landsat')
        logging.info("Beginning Downloads")
        for i in blob_names:
            blob = bucket.blob(i)
            filename = get_filename_from_blobname(i)
            blob.download_to_filename(download_dir / filename)
            logging.info('PathRow: {}{} \tDate: {} \tDownloaded to: {}'.format(path, row, date, download_dir))
        print("Done")
    else:
        print("No files to download")

# path, row =  get_pathrow_from_latlon(4.1761213,45.0235419)
# get_all_dates(path, row)
#get_bands('164', '57', '20141005', [1, 2, 3])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Download Landsat images")
    parser.add_argument("-d", metavar = "--downloadDir", type=str,
                        help="Directory to save downloaded files to")
    parser.add_argument("-p", metavar="--path", type=str,
                        help="Path of PathRow to get the image")
    parser.add_argument("-r", metavar="--row", type=str,
                        help="Row of PathRow to get image")
    parser.add_argument("-dt", metavar="--date", type=str,
                        help="Date to download images. Format: YYYYMMDD")
    parser.add_argument("-b", metavar="--bands", type=str,
                        help="List of band numbers to download. Sample: 1,2,3,4")
    args = parser.parse_args()
    
    bands = [int(i) for i in args.b.split(',')]
    download_dir = Path(args.d)
    get_bands(args.p, args.r, args.dt, bands, download_dir)
    