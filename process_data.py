import json
import os
import psutil
from utils.logger import logger

def update_file_crawled(page_name, video_id):
    folder_path = "data crawled"
    file_path = os.path.join(folder_path, f"{page_name}.txt")
    # Kiểm tra xem tệp tin đã tồn tại hay chưa
    if not os.path.exists(file_path):
        # Tạo tệp tin mới nếu chưa tồn tại
        try:
            with open(file_path, "w") as file:
                file.write(video_id + "\n")
        except Exception as e: 
            print(e)
    else:
        # Mở tệp tin và thêm video_id vào cuối tệp tin
        with open(file_path, "a") as file:
            file.write(video_id + "\n")

def write_post_to_file(post):
    with open("result.txt", "a", encoding="utf-8") as file:
        file.write(f"{str(post)}\n")
        if post.is_valid:
            file.write("🇧🇷" * 50 + "\n")
        else:
            file.write("🎈" * 50 + "\n")

def remove_key_value(dictionary, value):
    keys_to_remove = []
    for key, val in dictionary.items():
        if val == value:
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del dictionary[key]
        
def terminate_process_and_children(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)

        # Tắt tất cả các tiến trình con
        for child in children:
            child.terminate()
        # Chờ cho tất cả các tiến trình con kết thúc
        psutil.wait_procs(children)

        # Tắt tiến trình cha
        parent.terminate()
        parent.wait()
        logger.debug(f"Process with PID {pid} terminated.")
    except psutil.NoSuchProcess:
        logger.debug(f"No process found with PID {pid}.")
        
def check_memory_process(process_id):
    # Lấy thông tin về bộ nhớ của tiến trình
    process = psutil.Process(process_id)
    memory_info = process.memory_info()
    memory_usage = memory_info.rss / (1024 * 1024)  # Đơn vị: Megabyte
    logger.warning(f"Memory usage: {memory_usage} MB")
    return memory_usage

    # # Kiểm tra nếu bộ nhớ vượt quá giới hạn cho phép
    # if memory_usage > max_memory:
    #     logger.warning("Memory usage exceeded. Restarting the process...")
    #     terminate_process_and_children(pid=process_id)
    
    

    
