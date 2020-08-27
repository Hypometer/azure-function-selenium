import logging

import azure.functions as func
from selenium import webdriver
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import traceback
import os, time

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request. 11:38')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Something to check with fonts?

    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)

    try:
        url = req.params.get('url')
        width = int(req.params.get('size').split("-")[0])
        height = int(req.params.get('size').split("-")[1])
        urlextra = ""
        if req.params.get('sports') is not None:
            sports = req.params.get('sports')
            urlextra += '&sports='+sports
        if req.params.get('date') is not None:
            date = req.params.get('date')
            urlextra += '&date='+date
        if req.params.get('books') is not None:
            date = req.params.get('books')
            urlextra += '&books='+books

        newurl = url + urlextra

        logging.info('trying url', newurl)
        driver.get(newurl)
        driver.set_window_size(width,height)
        time.sleep(5)
        screenshot = driver.get_screenshot_as_png()

        # create blob service client and container client
        credential = DefaultAzureCredential()
        storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
        client = BlobServiceClient(account_url=storage_account_url, credential=credential)
        blob_name = url.split('azurewebsites.net/')[1].replace("/","-")+"-"+str(datetime.now())+".png"
        blob_client = client.get_blob_client(container=os.environ["par_storage_container_name"], blob=blob_name)
        blob_client.upload_blob(screenshot)

        return func.HttpResponse(
                str(blob_name),
                status_code=200
        )
    except Exception as e: 
        logging.error(e)
        track = traceback.format_exc()
        logging.error(track)
        logging.info('Something went very very wrong')
        raise