
from azure.storage.blob import BlobServiceClient, BlobClient

import os

BASE_PATH = os.path.dirname(os.path.realpath(__file__))

STORAGEACCOUNTURL = "https://talintelstore.blob.core.windows.net"
STORAGEACCOUNTKEY = "LuXmBbMyb2npuPG5rux0NrZGBvby1jNCWE44h1yLoUPxZ7nKnPCGHwiP4K0F3VOQOtOCbsmcLDxD+dpdYJNPLA=="

my_file = "Hormel-all_current.csv"
CONTAINERNAME = "ti-data"
BLOBNAME = "csv/pipeline/Hormel-all_current.csv"
BLOBSTART = "csv/pipeline/"

def proj_level(storageaccounturl = STORAGEACCOUNTURL, storageaccountkey = STORAGEACCOUNTKEY):
    BLOBNAME = BLOBSTART + "Project Level Reporting-all.csv"

    blob_service_client_instance = BlobServiceClient(account_url=storageaccounturl, credential=storageaccountkey)
    blob_client_instance = blob_service_client_instance.get_blob_client(CONTAINERNAME, BLOBNAME, snapshot=None)
    blob = blob_client_instance.download_blob().content_as_text()
    df = pd.read_csv(StringIO(blob))

    df = df.groupby("Linked pipeline")

    print (df)
