import os

import time
import schedule
import threading
import requests
import config.config as cfg

from bs4 import BeautifulSoup
from api_check_post import check_link_crawled
from browser import ChromiumBrowser
from crawl_post import CrawlPost
from datetime import datetime, timedelta
from es import get_link_es
from login import *
from playwright.sync_api import Page, Playwright
from queue import Queue
from utils.logger import logger


class SearchPlatform:
    def __init__(self, config) -> None:
        self.config = config
        self.link_queue_video = Queue()
        self.link_queue_photo = Queue()
        
    def init_browser(self, reset=0):
        proxy = self.config["account"]["proxy"]["http"]
        proxy = proxy.replace("http://", "")
        browser = ChromiumBrowser()
        browser.init(reset=reset)
        return browser
    
    def crawl_links_photo(self):
        browser = self.init_browser()
        # page = browser.context.new_page()
        # page.goto("https://www.tiktok.com/")
        while not self.link_queue_photo.empty():
            link = self.link_queue_photo.get()
            crawl = CrawlPost(url=link, mode=3)
            crawl.get_info_post(proxy=self.config["account"]["proxy"],browser=browser)
            del crawl
        # page.close()
        browser.context.close()
        browser.browser.close()
        del browser
            
    def crawl_links_video(self):
        while not self.link_queue_video.empty():
            link = self.link_queue_video.get()
            crawl = CrawlPost(url=link, mode=3)
            crawl.get_info_post(proxy=self.config["account"]["proxy"])
            del crawl
    
    def run(self):
        self.browser = self.init_browser()
        self.browser.page.goto("https://vt.tiktok.com/")
        try:
            login_with_cookies(page=self.browser.page, account=self.config["account"])
        except:
            get_cookies(page=self.browser.page, account=self.account)
        logger.debug("Done login")
        try:
            # self.browser.page.close()
            self.get_link_list(self.browser)
        except Exception as e:
            logger.warning(e)
        self.browser.page.close()
        self.browser.context.close()
        self.browser.browser.close()
        del self.browser
        self.get_thread()
        
    def get_thread(self):
        num_threads = 3  # Number of threads to create
        threads = []
        if self.link_queue_video.qsize() != 0:
            thread_a = threading.Thread(target=self.crawl_links_photo)
            thread_a.start()
            threads.append(thread_a)
        for _ in range(num_threads):
            thread = threading.Thread(target=self.crawl_links_video)
            thread.start()
            threads.append(thread)
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        logger.debug("Sleep 1 hour")
        time.sleep(60*60)
        return self.run()
    
class SearchUser(SearchPlatform):
    def __init__(self, config) -> None:
        super().__init__(config)
        
    def get_link_list(self, browser):
        list_user = self.config["mode"]["list_page"]
        for user in list_user:
            try:
                page = browser.context.new_page()
                page.goto(user)
                page.mouse.wheel(0, 200)
                time.sleep(5)
                solve_captcha.check_captcha(page)
                BOOL = True
                check = 0
                check_list = 1
                list_links_element = []
                list_links = []
                link_checked = []
                while len(list_links_element) != check_list and BOOL:
                    check_list = len(list_links_element)
                    page.mouse.wheel(0, 3000)
                    time.sleep(2)
                    list_links_element = page.query_selector_all('//*[@data-e2e="user-post-item-desc"]')
                    for link in list_links_element:
                        element = link.query_selector('a')
                        href = element.get_attribute('href')
                        if href not in link_checked:
                            check_link = check_link_crawled(link=href)
                            if check_link:
                                check += 1
                                link_checked.append(href)
                            else:
                                if href not in list_links:
                                    list_links.append(href)
                                    link_checked.append(href)
                        if check > 4:
                            BOOL = False
                            break
                        if len(list_links) > 100:
                            BOOL = False
                            break
                logger.debug(f"Count of {user} is {len(list_links)}")
                for link in list_links:
                    if "video" in link:
                        self.link_queue_video.put(link)
                    elif "photo" in link:
                        self.link_queue_photo.put(link)
                page.close()
                time.sleep(5)
            except Exception as e:
                logger.warning(e)
        logger.info(f"Len of link_queue_video {self.link_queue_video.qsize()}")
        logger.info(f"Len of link_queue_photo {self.link_queue_photo.qsize()}")
        
class SearchPost(SearchPlatform):
    def __init__(self, config) -> None:
        super().__init__(config)
        
  
    def get_link_list(self, browser):
        keywords = self.config["mode"]["keyword"] 
        proxies = self.config["account"]["proxy"]
        url = "https://www.google.com/search?q="
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
        }
        for keyword in keywords:
            try:
                # proxies = {
                #                 "http": "http://172.168.201.4:34001",
                #                 "https": "http://172.168.201.4:34001"
                #             }
                start_cur = 0
                while True:
                    params = {
                            'q': f'"{keyword}"',
                            'tbs': 'qdr:w,srcf:H4sIAAAAAAAAAC3KQQqAMAwF0dt0I_1ROaY0aapIqPwVvLxV3A28eD0ThXF0TRj-on0HIw9ICafD2yRVku5Eqr0ITES64eeZGlYv_14wvfk_1x6TwAAAA',
                            'tbm': 'vid',
                            'start': f'{start_cur}' 
                        }
                    # response = requests.get(url, proxies=cfg.proxies, headers=headers)
                    response = requests.get(url, params=params, headers=headers, proxies=proxies)
                    # Parse HTML content
                    soup = BeautifulSoup(response.text, 'html.parser')
                    results = []
                    # Iterate through search results
                    for i, g in enumerate(soup.find_all('div', class_='PmEWq')):
                        # Extract link, title, and snippet (if available)
                        link = g.find('a')['href']
                        if link not in results:
                            if "tiktok.com" in link and "/video/" in link:
                                results.append(link)
                        # Append result to list
                        # results.append(link)
                        # Limit to top 10 results
                    if len(results) >= 100:
                        break
                    elif start_cur >= 100:
                        break
                    else:
                        start_cur += 10
                logger.info(f"Len of video keyword {keyword} is {len(results)}")
                for link in results:
                    check_link = check_link_crawled(link=link)
                    if check_link:
                        continue
                    else:
                        self.link_queue_video.put(link)
                    # print(href)
            except Exception as e:
                logger.warn(f"Error to get {keyword} by Exception {e}")
                continue
        logger.info(f"Len of link_queue_video {self.link_queue_video.qsize()}")
            
            
class Update: 
    def __init__(self, config) -> None:
        self.config = config
        self.link_queue_video = Queue()
        self.link_queue_photo = Queue()
        
    def init_browser(self):
        proxy = self.config["account"]["proxy"]["http"]
        proxy = proxy.replace("http://", "")
        browser = ChromiumBrowser()
        browser.init()
        return browser
        
    def run(self):
        start_time_run = self.config["mode"]["start_time_run"]
        schedule.every().day.at(start_time_run).do(self.update_post)
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    def get_link_list_es(self):
        self.link_queue_video.queue.clear()
        self.link_queue_photo.queue.clear()
        range_date = self.config["mode"]["range_date"]
        format_str = "%m/%d/%Y %H:%M:%S"
        now = datetime.now()
        link_to_update = []
        for range_value in range_date:
            link=[]
            gte = now - timedelta(days=int(range_value))
            lte = now - timedelta(days=int(range_value)-1)
            gte = gte.replace(hour=0, minute=0, second=0, microsecond=0)
            lte = lte.replace(hour=0, minute=0, second=0, microsecond=0)
            gte_str = gte.strftime(format_str)
            lte_str = lte.strftime(format_str)
            logger.debug("Get link es")
            link = get_link_es(gte=gte_str, lte=lte_str)
            link_to_update.extend(link)
        link_to_update = list(set(link_to_update))
        for link in link_to_update:
            if "video" in link:
                self.link_queue_video.put(link)
            elif "photo" in link:
                self.link_queue_photo.put(link)
        logger.info(f"Len of link_queue_video {self.link_queue_video.qsize()}")
        logger.info(f"Len of link_queue_photo {self.link_queue_photo.qsize()}")
            
    def update_post(self):
        self.get_link_list_es()
        self.browser = self.init_browser()
        self.get_thread()
        
    def crawl_links_photo(self):
        browser = self.init_browser()
        while not self.link_queue_photo.empty():
            link = self.link_queue_photo.get()
            crawl = CrawlPost(url=link, mode=5)
            self.browser=crawl.get_info_post(proxy=self.config["account"]["proxy"],browser=browser)
            del crawl
        browser.context.close()
        browser.browser.close()
        del browser
            
    def crawl_links_video(self):
        while not self.link_queue_video.empty():
            link = self.link_queue_video.get()
            crawl = CrawlPost(url=link, mode=5)
            browser=crawl.get_info_post(proxy=self.config["account"]["proxy"])
            del crawl

    def get_thread(self):
        num_threads = 5  # Number of threads to create
        threads = []
        thread_a = threading.Thread(target=self.crawl_links_photo)
        thread_a.start()
        threads.append(thread_a)
        for _ in range(num_threads):
            thread = threading.Thread(target=self.crawl_links_video)
            thread.start()
            threads.append(thread)
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        logger.debug("Sleep 1 hour")
        time.sleep(60*60)
        return self.run()
                          

