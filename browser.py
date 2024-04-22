from playwright.sync_api import sync_playwright
import requests
import time
import json

class ChromiumBrowser:
    def init(self, proxy=None,reset=0,fake=0):
        self.browser = None
        self.context = None
        self.page = None
        self.proxy = proxy
        self.reset = reset
        self.fake= fake
        self.playwright = sync_playwright().start()
        self.init_browser()

    def init_browser(self):
        browser_args = [
            "--incognito",
           "--enable-automation",
           "--allow-pre-commit-input",
           "--no-first-run","--log-level=0",
           "--password-store=basic",
           "--use-mock-keychain",
           "--test-type=webdriver",
           "--enable-blink-features=ShadowDOMV0",
           "--no-service-autorun",
           "--ignore-certificate-errors",
           "--disable-setuid-sandbox",
           "--hide-scrollbars",
           "--disable-backgrounding-occluded-windows",
           "--disable-gpu",
           "--disable-permissions-api",
           "--disable-background-networking",
           "--enable-precise-memory-info",
           "--disable-client-side-phishing-detection",
           "--disable-default-apps",
           "--disable-hang-monitor",
           "--disable-translate",
           "--disable-prompt-on-repost",
           "--disable-sync",
           "--disable-popup-blocking",
           "--no-sandbox",
           "--no-zygote",
           "--load-extension=C:\\AD\\Osint\\playwright\\sonet-chromium_08112023\\nomovdo",
           "--sonet-diswebgl",
           "--js-flags=--max_old_space_size=800 --max_semi_space_size=800"
        ]
        
        # Thêm cấu hình proxy nếu biến 'self.proxy' không None
        launch_options = {
            'headless': True,
            'args': browser_args
        }
        if self.proxy:
            if self.reset==1:
                self.change_ip_proxy()
            status=self.check_status_proxy()
            if status == True:
                print(f"Proxy {self.proxy} is ready")
                launch_options['proxy'] = {'server': f'http://{self.proxy}'}
            else:
                pass

        self.browser = self.playwright.chromium.launch(**launch_options)
        self.context = self.browser.new_context()
        # if self.fake==1:
        #     cookies = [
        #     {'name': 'xfa_csrf', 'value': '4oIOs24YYqd1XKQ9', 'domain': 'xamvn.id', 'path': '/'},
        #     {'name': 'xfa_user', 'value': '525172%2CmJ0wpIY3taDYQeLXX-u_6_k85Ufc8VkIu52ynHmR', 'domain': 'xamvn.id', 'path': '/'},
        #     {'name': 'xfa_session', 'value': 'opUHHIMBdAMYHg08X8r2YnAlZKUgjHlN', 'domain': 'xamvn.id', 'path': '/','expiration':8841849156.843996}
        #     ]
        #     self.context.add_cookies(cookies)
        #     self.page = self.context.new_page()
        # else:
        self.page = self.context.new_page()
        # self.page.set_viewport_size(page_size={width=1280, height=720})
        try:
            self.page.set_viewport_size({"width": 1280, "height": 720})
        except Exception as e:
            print(e)
        # if self.fake==1:
        #     if len(pages) > 1:
        #         pages[0].close()
        
        
    def change_ip_proxy(self):
        print(f"Change IP Public of Proxy: {self.proxy}")
        port=str(self.proxy).split(':')[-1]
        url = f'http://172.168.201.2:6868/reset?proxy={port}'
        response = requests.post(url)
        time.sleep(30)
    def check_status_proxy(self):
        print(f"Check status proxy {self.proxy}")
        url=f'http://172.168.201.2:6868/status?proxy={self.proxy}'
        response = requests.post(url)
        json_res=json.loads(response.text)
        if json_res['status'] is True:
            return True
        else:
            return False