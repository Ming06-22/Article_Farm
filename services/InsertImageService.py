import json

from typing import List

from services.interface.AssistantInterface import AssistantInterface
from utils.LogUtil import LogUtil
from utils.YamlUtil import YamlUtil

class InsertImageService(AssistantInterface):
    def __init__(self, yaml: YamlUtil):
        super().__init__(yaml, 'insert_image')
        self.log_util = LogUtil(__name__)
    
    def start_assistant(self, file_paths: List[str], prompt: str = None) -> str:
        while True:
            self.log_util.record_info("insert image in content")
            # upload file
            self.upload_file(file_paths)
            # create thread
            self.create_thread()
            
            # run assistant
            self.run_assistant()
            # get result
            result = self.get_assistant_response()
            
            # delete assistant vector space
            self.delete_file()
            
            try:
                json.loads(result)
                return result
            except:
                pass