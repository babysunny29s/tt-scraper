import os
import config.config as cf
import requests

from utils.logger import logger


api_address=cf.api_address


def get_links(table_name, object_id):
    url = f"{api_address}/get-links/{table_name}/{object_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return{}
    except requests.exceptions.RequestException as e:
        return {}

# API insert link đã crawl vào db
def insert(table_name, object_id, links):
    # return True
    if api_address == "":
        logger.warning("Cant insert api because dont have api address")
    else:
        if isinstance(links, list):
            links = ",".join(links)
        url = f"{api_address}/insert/{table_name}/{object_id}?new_links={links}"
        try:
            response = requests.post(url)
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error: {str(e)}")
    
def check_link_crawled(link):
    # return False
    page_name = link.split('@')[1].split('/')[0]
    video_id = link.split('/')[-1]
    try:
        data_crawled = get_links(table_name="tiktok_video", object_id= page_name)
        if data_crawled:
            if "links" in data_crawled:
                if video_id in data_crawled["links"]:
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    except Exception as e:
        logger.error("Cant check link in api")
        folder_path = "data crawled"
        # Kiểm tra xem file có tên trùng với page_name tồn tại trong thư mục hay không
        file_path = os.path.join(folder_path, f"{page_name}.txt")
        if not os.path.exists(file_path):
            return False
        # Đọc nội dung của file
        with open(file_path, "r") as file:
            content = file.read().splitlines()
        # Kiểm tra xem video_id có trùng với phần tử nào trong nội dung hay không
        if video_id in content:
            return True
        return False
        