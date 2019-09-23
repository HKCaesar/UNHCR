from google.cloud import storage
# Set up google cloud api: https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python
import datetime as dt

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
    prefix = 'LC08/01/{}/{}/'.format(path, row)
    blobs = list_blobs_with_prefix('gcp-public-data-landsat', prefix)
    dates = list(set(i.name.split('/')[-1].split('_')[3] for i in blobs))
    dates = [dt.datetime.strptime(i, '%Y%m%d') for i in dates]
    return dates

# get_all_dates('163', '057')