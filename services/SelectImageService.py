from typing import List

from services.interface.AssistantInterface import AssistantInterface
from utils.LogUtil import LogUtil
from utils.YamlUtil import YamlUtil

class SelectImageService(AssistantInterface):
    def __init__(self, yaml: YamlUtil):
        super().__init__(yaml, 'select_image')
        self.log_util = LogUtil(__name__)

    def start_assistant(self, file_paths: List[str], prompt:str = None) -> str:
        self.log_util.record_info("select propriate image")
         # upload file
        self.upload_file(file_paths)
        # create thread
        self.create_thread()
        while True:
            # run assistant
            self.run_assistant()
            # get result
            result = self.get_assistant_response()
            if len(result.split(',')) == 3:
                break
        # delete assistant vector space
        self.delete_file()
        
        return result