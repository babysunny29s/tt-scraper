import datetime
from post_extractor import PostExtractor
import json
from utils.logger import logger
import time

def extract_timestamp(value):
    if isinstance(value, datetime.datetime):
        value = int(value.timestamp())
    elif isinstance(value, float):
        value = int(value)
    elif not str(value).isdigit():
        try:
            value = int(datetime.datetime.strptime(str(value), "%m/%d/%Y %H:%M:%S").timestamp())
        except ValueError:
            return None
    return value

class PostTikTokExtractor(PostExtractor):
    def __init__(self, link, source_id, infor_text):
        super().__init__()
        self.link = link
        self.source_id = source_id
        self.infor_text = infor_text
          
    def extract_post_link(self):
        return self.link
    
    def extract_post_id(self):
        id = "tt_" + self.source_id
        return id

    def extract_post_time_crawl(self):
        time_crawl = datetime.datetime.now()
        time_crawl = extract_timestamp(time_crawl)
        return time_crawl

    def extract_post_author(self):
        author = self.infor_text["author"]["nickname"]
        return author

    def extract_post_author_link(self):
        author_link = "https://www.tiktok.com/@" + self.infor_text["author"]["uniqueId"]
        return author_link

    def extract_post_author_avatar(self):
        avatar = self.infor_text["author"]["avatarThumb"]
        # avatar = avatar.get_attribute('src')
        return avatar

    def extract_post_created_time(self):
        createTime = self.infor_text["createTime"]
        createTime = extract_timestamp(createTime)
        return createTime

    def extract_post_content(self):
        return ""
    
    def extract_post_image_url(self):
        image_url = []
        if "photo" in self.link:
            image_post=self.infor_text["imagePost"]["images"]
            for image in image_post:
                image_url.append(image["imageURL"]["urlList"][0])
        return image_url
    
    def extract_post_title(self):
        title = self.infor_text["desc"]
        return title

    def extract_post_like(self):
        like = int(self.infor_text["stats"]["diggCount"])
        return like

    def extract_post_love(self):
        love = int(self.infor_text["stats"]["collectCount"])
        return love

    def extract_post_comment(self):
        comment = int(self.infor_text["stats"]["commentCount"])
        return comment

    def extract_post_share(self):
        share = int(self.infor_text["stats"]["shareCount"])
        return share

    def extract_post_domain(self):
        domain = "www.tiktok.com"
        return domain

    def extract_post_hashtag(self):
        try:
            data = self.infor_text["textExtra"]
        except:
            data = None
        if data is not None:
            hashtag =  [f'#{item["hashtagName"]}' for item in data]
        else:
            hashtag = []
        return hashtag

    def extract_post_music(self):
        music = "https://www.tiktok.com/music/" + self.infor_text["music"]["title"] + "-" + self.infor_text["music"]["id"]
        return music

    def extract_post_duration(self):
        duration = int(self.infor_text["video"]["duration"])
        return duration

    def extract_post_view(self):
        view = int(self.infor_text["stats"]["playCount"])
        return view

    def extract_post_type(self):
        if "photo" in self.link:
            type = "tiktok photo"
        elif "video" in self.link:
            type = "tiktok video"
        return type

    def extract_post_source_id(self):
        source_id = ""
        return source_id


class PostCommentExtractor(PostExtractor):
    def __init__(self,comment_dict):
        self.comment_dict = comment_dict

    def extract_post_link(self):
        return ""

    def extract_post_id(self):
        id = "tt_" + self.comment_dict["cid"]
        return id

    def extract_post_time_crawl(self):
        time_crawl = datetime.datetime.now()
        time_crawl = extract_timestamp(time_crawl)
        return time_crawl

    def extract_post_author(self):
        author = self.comment_dict["user"]["nickname"]
        return author
    
    def extract_post_title(self):
        return ""

    def extract_post_author_link(self):
        author_link = "https://www.tiktok.com/@" + self.comment_dict["user"]["unique_id"]
        return author_link

    def extract_post_author_avatar(self):
        try:
            avatar = self.comment_dict["user"]["avatar_thumb"]["url_list"][0]
            return avatar
        except:
            return ""

    def extract_post_created_time(self):
        createTime = self.comment_dict["create_time"]
        createTime = extract_timestamp(createTime)
        return createTime
    
    def extract_post_content(self):
        content = self.comment_dict["text"]
        return content
    
    def extract_post_image_url(self):
        return []

    def extract_post_like(self):
        like = self.comment_dict["digg_count"]
        return like

    def extract_post_love(self):
        return 0

    def extract_post_comment(self):
        comment = self.comment_dict["reply_comment_total"]
        return comment

    def extract_post_share(self):
        return 0

    def extract_post_domain(self):
        domain = "www.tiktok.com"
        return domain

    def extract_post_hashtag(self):
        return []

    def extract_post_music(self):
        return ""

    def extract_post_duration(self):
        return 0

    def extract_post_view(self):
        return 0

    def extract_post_type(self):
        type = "tiktok comment"
        return type

    def extract_post_source_id(self):
        # getIDvid = self.driver.find_element(
        #     By.XPATH, '//*[@class="tiktok-web-player no-controls"]')
        # source_id = "tt_" + ((getIDvid.get_attribute('id')).split('-'))[2]
        # sed = self.link.split('/')
        # source_id = sed[-1]
        source_id = "tt_" + self.comment_dict["aweme_id"]
        return source_id

class PostReplyExtractor(PostExtractor):
    # POST_AUTHOR_XPATH: str = './/a[not(contains(@href, "group")) and not(@href="#")]'
    def __init__(self,reply_dict):
        self.reply_dict = reply_dict
       
    def extract_post_link(self):
        return ""

    def extract_post_id(self):
        id = "tt_" + self.reply_dict["reply_id"] + "." + self.reply_dict["cid"]
        return id

    def extract_post_time_crawl(self):
        time_crawl = datetime.datetime.now()
        time_crawl = extract_timestamp(time_crawl)
        return time_crawl

    def extract_post_author(self):
        author = self.reply_dict["user"]["nickname"]
        return author
    
    def extract_post_title(self):
        return ""

    def extract_post_author_link(self):
        author_link = "https://www.tiktok.com/@" + self.reply_dict["user"]["unique_id"]
        return author_link

    def extract_post_author_avatar(self):
        try:
            avatar = self.reply_dict["user"]["avatar_thumb"]["url_list"][0]
            return avatar
        except:
            return ""

    def extract_post_created_time(self):
        createTime = self.reply_dict["create_time"]
        createTime = extract_timestamp(createTime)
        return createTime

    def extract_post_content(self):
        content = self.reply_dict["text"]
        return content
    
    def extract_post_image_url(self):
        return []

    def extract_post_like(self):
        like = self.reply_dict["digg_count"]
        return like

    def extract_post_love(self):
        return 0

    def extract_post_comment(self):
        # comment = self.comment
        return 0

    def extract_post_share(self):
        return 0

    def extract_post_domain(self):
        domain = "www.tiktok.com"
        return domain

    def extract_post_hashtag(self):
        return []

    def extract_post_music(self):
        return ""

    def extract_post_duration(self):
        return 0

    def extract_post_view(self):
        return 0

    def extract_post_type(self):
        type = "tiktok comment"
        return type

    def extract_post_source_id(self):
        source_id = "tt_" + self.reply_dict["aweme_id"]
        return source_id