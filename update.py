import json
import config.config as cfg

from manage_crawl import Update

if __name__ == "__main__":
    with open(cfg.config_update_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    crawl = Update(config)
    crawl.run()