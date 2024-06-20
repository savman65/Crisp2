import pandas as pd

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

import os

import time


storage_account_name = os.getenv('crispsa')
storage_account_key = os.getenv('crispsakey')

#for local testing
#storage_account_key = ""
#storage_account_name = "crispsadsavitz"

source_container_name = "csv"
destination_container_name = "parquet"
local_target_directory = "./blob_files/"
saPollingIntervalSeconds = 5
connection_string = f"DefaultEndpointsProtocol=https;AccountName={storage_account_name};AccountKey={storage_account_key};EndpointSuffix=core.windows.net"
#blobName = os.getenv('crispsablobname')

blobRecord = []
blobsToProcessNow = []


def download_blob(storage_account_name, storage_account_key, container_name, local_target_directory):
    # Construct the BlobServiceClient using the account key
    global blobRecord
    global blobsToProcessNow
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=storage_account_key
    )

    container_client = blob_service_client.get_container_client(container_name)

    blob_list = container_client.list_blobs()

    # Download each blob to local directory
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob)
        download_file_path = local_target_directory + blob.name

        print(f"Downloading blob to {download_file_path}")

        with open(download_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

        print(f"Downloaded {blob.name} to {download_file_path}")
        
        if blob.name not in blobRecord:
            blobsToProcessNow.append(blob.name)
            blobRecord.append(blob.name)
        print(f"blob recorded so far: {blobRecord}")
        print(f"converting the following blobs to parquet now: {blobsToProcessNow}")

def upload_blob_to_azure(connection_string, container_name, blob_name, parquet_file_path):
    global blobRecord
    global blobsToProcessNow
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    
    with open(parquet_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

if __name__ == "__main__":
    while True:
        #try: 
        download_blob(storage_account_name, storage_account_key, source_container_name, local_target_directory)

        for blob in blobsToProcessNow:
            # Read CSV file into pandas DataFrame
            blobNoExt = blob.replace(".csv", "")
            df = pd.read_csv(f"{local_target_directory}/{blobNoExt}.csv")

            # Specify the output Parquet file
            #parquet_file = '{blobName}.parquet'

            #pyarrow for Parquet writing
            df.to_parquet(f"{local_target_directory}/{blobNoExt}.parquet", engine='pyarrow')

            # Option 2: Using fastparquet for Parquet writing
            # Ensure to have fastparquet installed: pip install fastparquet
            # df.to_parquet(parquet_file, engine='fastparquet')

            print(f"CSV file '{blobNoExt}.csv' converted to Parquet file '{blobNoExt}.parquet' successfully.")

            upload_blob_to_azure(connection_string, destination_container_name, f"{blobNoExt}.parquet", f"./{local_target_directory}/{blobNoExt}.parquet")

        blobsToProcessNow = []
        #except Exception as e:
        #    print("failed")
        time.sleep(saPollingIntervalSeconds)














