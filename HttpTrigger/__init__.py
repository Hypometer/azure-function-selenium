import logging

import azure.functions as func
from selenium import webdriver
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request. 11:38')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)

    url = req.params.get('url')
    width = req.params.get('size').split("-")[0]
    height = req.params.get('size').split("-")[1]

    driver.get(url)
    # links = driver.find_elements_by_tag_name("a")
    # link_list = ""
    # for link in links:
    #     if link_list == "":
    #         link_list = link.text
    #     else:
    #         link_list = link_list + ", " + link.text
    driver.set_window_size(width,height)
    screenshot = driver.get_screenshot_as_png()

    # create blob service client and container client
    credential = DefaultAzureCredential()
    storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
    client = BlobServiceClient(account_url=storage_account_url, credential=credential)
    blob_name = url.split('azurewebsites.net/')[1].replace("/","-")+".png"
    blob_client = client.get_blob_client(container=os.environ["par_storage_container_name"], blob=blob_name)
    blob_client.upload_blob(screenshot)

    return func.HttpResponse(
             str(blob_name),
             status_code=200
    )