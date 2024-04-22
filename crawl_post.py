import os
import pickle
import requests

import json
import time

import config.config as cfg
import captcha.captcha as solve_captcha


from api_check_post import insert
from browser import ChromiumBrowser
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from process_data import *
from post_tiktok_etractor import PostTikTokExtractor, PostCommentExtractor, PostReplyExtractor
from utils.logger import logger
from urllib.parse import urlencode as encoder

  
producer = KafkaProducer(bootstrap_servers=[cfg.kafa_address])


class CrawlPost:
    def __init__(self,url,mode) -> None:
        self.url = url
        self.mode = mode
        
    # def init_browser(self):
    #     proxy = cfg.proxies_photo
    #     browser = ChromiumBrowser()
    #     browser.init(proxy=proxy)
    #     return browser
      
    def get_info_post(self,proxy=0, browser=None):
        try:
            start = time.time()
            post_id = self.url.split("/")[5].split("?", 1)[0]
            page_name = self.url.split('@')[1].split('/')[0]
            if "video" in self.url:
                post = self.get_info_video(proxy= proxy,video_id=post_id)
            if "photo" in self.url:
                post = self.get_info_post_photo(browser, post_id=post_id)
            if post is not None:
                self.push_kafka(type="post", obj=post)
                write_post_to_file(post=post)
                if self.mode != 5:
                    try:
                        update_file_crawled(page_name=page_name, video_id=post_id)
                    except:
                        logger.warning("Cant insert link to local database")
                    try:
                        insert_post = insert(table_name="tiktok_video", object_id=page_name, links=post_id)
                    except:
                        logger.warning("Cant insert link to api")
                self.get_comments_and_replies(proxy=proxy, post_id=post_id)
            end = time.time()
            logger.info(f"Time crawl {self.url} is {end -start}")
        except:
            logger.warn(f"Error to crawl {self.url}")
        
    
    def get_info_video(self, proxy, video_id):
        logger.debug(f"Start crawl link {self.url}")
        try:
            proxies = {
                'http': 'http://172.168.201.2:4010',
                'https': 'http://172.168.201.2:4010'
            }
            posts = []
            headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "authority": "www.tiktok.com",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Host": "www.tiktok.com",
                "User-Agent": "Mozilla/5.0  (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) coc_coc_browser/86.0.170 Chrome/80.0.3987.170 Safari/537.36",
            }
            # res = requests.get(url=self.url, headers=headers, proxies=proxies)
            res = requests.get(url=self.url, headers=headers)
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
            json_data = script_tag.string.strip()
            json_data = json.loads(json_data)
            infor_text = json_data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
            post_extractor: PostTikTokExtractor = PostTikTokExtractor(link=self.url,source_id=video_id ,infor_text=infor_text)
            post = post_extractor.extract()
            del post_extractor
            if post is not None:
                return post
            else: 
                return None
        except Exception as e:
            logger.warning(e)
            
    # def handle_response(self, response, info_json):
    #     if "/api/item/detail/?WebIdLastTime" in response.url:
    #         info_json = response.json()
    def handle_response(self,response, info_json):
        def get_response():
            if "/api/item/detail/?WebIdLastTime" in response.url:
                # print(f"{response.json()}\n")
                info_json.append(response.json())
        get_response()
            
    def get_info_post_photo(self,browser, post_id,post=None):
        # browser = self.init_browser()
        logger.debug(f"Start crawl link {self.url}")
        count = 0
        info_json = []
        page = browser.context.new_page()
        listen_response = lambda response: self.handle_response(response,info_json)
        page.on("response", listen_response)  
        page.goto(self.url)
        time.sleep(3)
        solve_captcha.check_captcha(page=page)
        browser.page.reload()
        while (len(info_json) == 0) and count < 4:
            count += 1
            time.sleep(3)
        if info_json:
            infor_text = info_json[0]["itemInfo"]["itemStruct"]
            post_extractor: PostTikTokExtractor = PostTikTokExtractor(link=self.url,source_id=post_id ,infor_text=infor_text)
            post = post_extractor.extract()
            del post_extractor
        else:
            post = None 
        page.remove_listener("response", listen_response)
        page.close()
        # browser.context.close()
        # browser.browser.close()
        # del browser
        if post:
            return post
      
    def get_comments_and_replies(self, proxy,post_id):
        try:
            logger.debug(f"Start crawl comments {self.url}")
            replies = []
            comments, cmt_ids = self.crawl_comment(proxy=proxy,post_id=post_id)
            for comment in comments:
                self.push_kafka(type="comment", obj=comment)
            if self.mode == 5:
                logger.debug(f"Start crawl replies {self.url}")
                for cmt_id in cmt_ids:
                    replies = self.crawl_reply(proxy=proxy,cmt_id=cmt_id)
                    for reply in replies:
                        self.push_kafka(type="comment", obj=reply)
        except Exception as e:
            logger.warning(f"Stop crawl comment of {self.url} by {e}")
    
    def push_kafka(self, type, obj):
        try:
            if self.mode == 5:
                topic = "osint-posts-update"
            elif type == "comment":
                topic = "osint-posts-update"
            else:
                topic = "osint-posts-raw"
            logger.info(f"Push {type} to kafka topic {topic} ")
            bytes_obj = pickle.dumps([obj.__dict__])
            producer.send(topic, bytes_obj)
            producer.flush()
        except Exception as e:
            logger.error(f"Fail to push {type} to kafka {topic}")
    
    def crawl_comment(self,proxy, post_id):
        comments =[]
        t = 0
        cmt_ids = []
        proxy = {
                'http': 'http://172.168.201.2:4010',
                'https': 'http://172.168.201.2:4010'
            }
        while True:
            try:
                headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                'referer': f'{self.url}',
            }
                # response_cmt = requests.get(f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={post_id}&count=999999&cursor={t}", headers=headers, proxies=proxy).json()
                response_cmt = requests.get(f"https://www.tiktok.com/api/comment/list/?aid=1988&aweme_id={post_id}&count=999999&cursor={t}", headers=headers).json()
                list_comments = response_cmt["comments"]
                if list_comments is not None:
                    for comment_dict in list_comments:
                        comment_extractor: PostCommentExtractor = PostCommentExtractor(comment_dict=comment_dict)
                        comment = comment_extractor.extract()
                        del comment_extractor
                        write_post_to_file(comment)
                        comments.append(comment)
                        reply = int(comment_dict["reply_comment_total"])
                        if reply > 0:
                            id = comment_dict["cid"]
                            cmt_ids.append(id)
                    t += 50
                else:
                    break
            except Exception as e:
                logger.warn(f"Error to crawl cmt by {e}")
        return comments, cmt_ids
            
    def crawl_reply(self, proxy, cmt_id):
        comments = []
        cus = 0
        headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                'referer': f'{self.url}',
            }
        proxy = {
                'http': 'http://172.168.201.2:4007',
                'https': 'http://172.168.201.2:4007'
            }
        while True:
            try:
                # reply_response = requests.get(f"https://www.tiktok.com/api/comment/list/reply/?aid=1988&comment_id={cmt_id}&count=100&cursor={cus}", headers=headers, proxies=proxy).json()
                reply_response = requests.get(f"https://www.tiktok.com/api/comment/list/reply/?aid=1988&comment_id={cmt_id}&count=100&cursor={cus}", headers=headers).json()
                list_reply = reply_response["comments"]
                if list_reply:
                    if len(list_reply) != 0:
                        for reply_dict in list_reply:
                            reply_extractor: PostReplyExtractor = PostReplyExtractor(reply_dict=reply_dict)
                            reply = reply_extractor.extract()
                            write_post_to_file(reply)
                            del reply_extractor
                            comments.append(reply)    
                        cus += 50
                    else:
                        break
                else:
                    break
            except Exception as e:
                logger.warn(f"Error crawl reply by {e}")
        return comments
            
    
if __name__ == "__main__":
    # proxy = "192.168.143.102:4003"
    # browser = ChromiumBrowser()
    # browser.init(proxy=proxy)
    # browser.page.goto("https://www.tiktok.com/")
    # time.sleep(5)
    # browser.page.goto("https://tiktok.com/@_vinhhoang01er_/video/7346066569534999816")
    # time.sleep(5)
    # solve_captcha.check_captcha(browser.page)
    # browser.page.close()
    with open("links_user.txt", "r") as file:
        lines = file.readlines()
        list_link = [line.strip() for line in lines]
    for link in list_link:
        crawl = CrawlPost(url = link, mode = 3)
        crawl.get_info_post()
        del crawl