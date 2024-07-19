import logging

class LogUtil():
    def __init__(self, log_name: str, log_file_path: str = '') -> None:
        self.log_file_path = log_file_path
        #self.file_hanlder = logging.FileHandler(self.log_file_path)
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(logging.INFO)
        self.stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.stream_handler.setFormatter(formatter)
        self.logger.addHandler(self.stream_handler)

    def record_info(self, text: str) -> None:
        self.logger.info(text)
    
    def record_error(self, text: str) -> None:
        self.logger.error(text, exc_info=True)