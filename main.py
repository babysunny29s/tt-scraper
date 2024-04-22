import json
import time
import psutil

import multiprocessing as mp

from process_data import *
from utils.logger import logger
from manage_crawl import SearchUser, SearchPost, Update
from playwright.sync_api import sync_playwright

class ProcessManager:
    def __init__(self):
        # List of running processes {id_config_running: pid_process}
        self.running_processes = dict()

    def is_process_running(self, pid):
        try:
            process = psutil.Process(pid)
            return process.is_running()
        except psutil.NoSuchProcess:
            return False

    def get_pid_by_name(self, process_name):
        for process in psutil.process_iter(['pid', 'name']):
            if process.info['name'] == process_name:
                return process.info['pid']
        return None

    def process_crawl(self, config, config_id):
        process_name = f"Process {config_id}"
        pid = self.get_pid_by_name(process_name)
        mode = config["mode"]["id"]
        if mode == 3 :
            crawl = SearchUser(config)
        if mode == 4:
            crawl = SearchPost(config)
        if mode == 5:
            crawl = Update(config)
        crawl.run()
        
    def manage_process(self):
        while True:
            # Check config from web
            with open("config/dev_config.json", "r", encoding="utf-8") as list_config_file:
                list_config_data = json.load(list_config_file)
            # Get list config id 
            list_config_id = list()
            for config in list_config_data:
                config_id = config.get("id")
                list_config_id.append(config_id)
                # Check to create new process is in config
                if config_id not in self.running_processes:
                    process = mp.Process(target=self.process_crawl, args=(config, config_id), name = f"Process {config_id}")
                    process.start()
                    self.running_processes[config_id] = process.pid
                    logger.debug(f"Create new process with id config: {config_id} and pid process: {process.pid}")
            # Check to terminate processes that no longer exist in the config file
            list_process_to_remove = list()
            if self.running_processes:
                for id_config_running, pid_process in self.running_processes.items():
                    if id_config_running not in list_config_id:
                        logger.debug(f"Kill process with id config: {id_config_running} and PID process: {pid_process}")
                        terminate_process_and_children(pid_process)      
                    if self.is_process_running(pid_process) is False:
                        list_process_to_remove.append(pid_process)
                        continue
            for pid_process in list_process_to_remove:
                remove_key_value(self.running_processes, pid_process)
                logger.debug(f"Process {pid_process} is not running")
            time.sleep(10)

if __name__ == '__main__':
    process_manager = ProcessManager()
    process_manager.manage_process()