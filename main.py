import os
import json
from cmath import log

from services.AnalyzeImageService import AnalyzeImageService
from services.ChatbotService import ChatbotService
from services.GoogleSearchService import GoogleSearchService
from services.GatherContentService import GatherContentService
from services.InsertImageService import InsertImageService
from services.SelectImageService import SelectImageService
from services.WordpressService import WordpressService
from services.SummaryArticleService import SummaryArticleService
from utils.FileUtil import FileUtil
from utils.FunctionsUtil import FunctionsUtil
from utils.LogUtil import LogUtil
from utils.YamlUtil import YamlUtil

if __name__ == "__main__":
    # initial util instance
    yaml_util = YamlUtil('./config.yaml')
    functions_util = FunctionsUtil()
    log_util = LogUtil(__name__)
    file_util = FileUtil()

    # initial service instance
    wordpress_service = WordpressService(yaml_util)
    google_search_service = GoogleSearchService()
    chatbot_service = ChatbotService(yaml_util, "openai")
    gather_content_service = GatherContentService(yaml_util)
    analyze_image_service = AnalyzeImageService(yaml_util)
    summary_article_service = SummaryArticleService(yaml_util)
    insert_image_service = InsertImageService(yaml_util)
    select_image_service = SelectImageService(yaml_util)

    try:
        functions_util.clear_console()

        # 顯示歡迎訊息
        print("歡迎使用AI 文章生成器")

        # 獲取當前檔案的目錄
        code_dir = os.path.dirname(os.path.abspath(__file__))

        # 構建相對路徑
        img_dir = os.path.join(code_dir, '.', "resources", "img")
        website_content_result_dir = os.path.join(code_dir, '.', "resources", "website_content.json")
        website_image_result_dir = os.path.join(code_dir, '.', "resources", "website_image.json")
        article_result_dir = os.path.join(code_dir, '.', "resources", "article.txt")
        
        if os.path.exists(img_dir):
            file_util.delete_file(img_dir)
        
        if os.path.exists(website_content_result_dir):
            file_util.delete_file(website_content_result_dir)
        
        if os.path.exists(website_image_result_dir):
            file_util.delete_file(website_image_result_dir)

        if os.path.exists(article_result_dir):  
            file_util.delete_file(article_result_dir)
        
        # ------------ 分析相關搜尋詞，爬取網站文章內容 ------------
        
        # target article category
        article_category = '新機情報'
        
        # target keyword
        key_word = '國際漫遊esim卡'

        # get article_category and prompt
        category_id, prompt = yaml_util.get_article_category(article_category)
        prompt = f"請幫我撰寫一篇有關{key_word}的文章" + prompt
        
        # get keywords list
        keywords = chatbot_service.expand_keyword(key_word)

        # get urls list
        urls = google_search_service.google_search(keywords)

        # get content text
        content = gather_content_service.thread_gather_website_content(urls)
        
        # write content text in json
        file_util.write_file("./resources/website_content.json", content)
        
        # ------------ 文章分析取得文章内容，並進行圖片分析，選擇合適的圖諞，生成文章摘要，上傳到WordPress網站，並發布文章 ------------
        
        # OpenAI Assistant summary 
        summary = summary_article_service.start_assistant(["./resources/website_content.json"], prompt)
        
        # split title and content
        title = summary[0][0]["content"]
        content = summary[1: ]
        content = str(content).replace("'","\"")
        
        # write content text in txt
        file_util.write_file("./resources/article.txt", content)
        
        # insert image in content
        content = insert_image_service.start_assistant(["./resources/article.txt"])

        # get the outline of paragraph
        paragraph = chatbot_service.conclude_paragraph(content, yaml_util.get_value("ai_key", "gemini")[0])
        img = google_search_service.google_search_image(paragraph)
        
        # detect image is valid or not
        img = gather_content_service.thread_is_valid_image_url(img)
        
        # download image  
        gather_content_service.thread_download_img(img) 
   
        # write content text in txt
        file_util.write_file("./resources/article.txt", content)
        
        # Google Gemini evaluate image score
        image_scores = analyze_image_service.thread_evaluate(content)

        target_image = functions_util.extract(image_scores)

        # write content text in json
        file_util.write_file("./resources/website_image.json", target_image)
        
        # OpenAI Assistant select image
        select_image = select_image_service.start_assistant(["./resources/website_image.json", "./resources/article.txt"])
        selected_image = functions_util.split_select_image(select_image)

        img_url = wordpress_service.add_image(selected_image)
        content = functions_util.replace_content_img(img_url, content)

        # post article into WordPress website
        wordpress_service.create_wordpress_post(title, content, category_id)
        
    except Exception as e:
        log_util.record_error(e)