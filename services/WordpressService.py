import requests
import base64
import os
import sys

from typing import List
from unicodedata import category
from pathlib import Path
from urllib3.exceptions import InsecureRequestWarning

from utils.LogUtil import LogUtil
from utils.YamlUtil import YamlUtil

sys.path.append(str(Path(__file__).resolve().parent.parent))

class WordpressService():
    def __init__(self, yaml: YamlUtil) -> None:
        self.log_util = LogUtil(__name__)
        self.wp_user = yaml.get_value("wordpress", "user")
        self.wp_password = yaml.get_value("wordpress", "password")
        self.wp_domain = yaml.get_value("wordpress", "domain")
        self.wp_url = self.wp_domain + "wp-json/wp/v2/posts/"
        self.wp_credentials = self.wp_user + ":" + self.wp_password
        self.wp_token = base64.b64encode(self.wp_credentials.encode())
        self.wp_header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Authorization": "Basic " + self.wp_token.decode("utf-8")
        }

    def create_wordpress_post(self, title: str, content: str, category: str, tag: str ="37") -> None:
        self.log_util.record_info("post article into wordpress")
        data = {
            "title": title,
            "status": "publish",
            "slug": "test-wp-rest-api",
            "content": content,
            "categories": category,
            "tags": "37,38"
        }
        requests.post(self.wp_url, headers = self.wp_header, json = data, verify = False)

    def update_wordpress_post(self) -> None:
        post_id = "1036"
        data = {
            "title": "更新測試文章標題",
            "status": "draft",
            "slug": "update_test-wp-rest-api",
            "content": "更新，這是測試文章內容",
        }

        response = requests.post(self.wp_url + post_id, headers = self.wp_header, json = data, verify = False)

    def delete_wordpress_post(self) -> None:
        post_id = ""
        response = requests.delete(self.wp_url + post_id, headers = self.wp_header, verify = False)

    def add_image(self, images: List[str]) -> List[str]:
        # 禁用 InsecureRequestWarning
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        image_url = []
        for image in images:
            feauturedfile_extension = os.path.splitext(image)[1]
            upload_image_url = self.wp_domain + "wp-json/wp/v2/media"
            code_dir = os.path.dirname(os.path.abspath(__file__))
            img_dir = os.path.join(code_dir,'..')  
            img_path = os.path.join(img_dir, image)

            headers = { 
                "Authorization": "Basic " + self.wp_token.decode("utf-8"),
                'Content-Type': 'image/{}'.format(feauturedfile_extension[1:]),  # 移除點號
                'Content-Disposition': 'attachment; filename="{}"'.format(os.path.basename(image))  # 只使用檔案名
            }
            
            img_data = open(img_path, 'rb').read()

            response = requests.post(url=upload_image_url, headers=headers, data=img_data, verify=False)
            if response.status_code == 201:
                image_url.append(response.json()['source_url'])
                print(f'圖片已上傳，URL: {image_url}')
            else:
                print(f'上傳失敗，錯誤碼: {response.status_code}')
                print(f'錯誤訊息: {response.text}')
                
        return image_url