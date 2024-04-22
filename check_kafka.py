from kafka import KafkaConsumer, TopicPartition
import pickle
import ast
def get_latest_offsets(bootstrap_servers, topic, partition):
    consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers)

    topic_partition = TopicPartition(topic, partition)

    consumer.assign([topic_partition])

    consumer.seek_to_end(topic_partition)
    latest_offset = consumer.position(topic_partition)
    consumer.close()

    return latest_offset
bootstrap_servers = '172.168.200.202:9092'
topic = 'osint-posts-raw'
partition = 0 
def consume_and_write_to_file(bootstrap_servers, topic, partition, start_offset, end_offset, output_file):
    consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers)
    topic_partition = TopicPartition(topic, partition)
    consumer.assign([topic_partition])
    consumer.seek(topic_partition, start_offset)
    try:
        with open(output_file, 'w') as file:
            for message in consumer:
                if message.offset >= end_offset:
                    break

                # Ghi tin nhắn vào tệp tin
                data = pickle.loads(message.value)
                if isinstance(data, list):
                    with open(output_file, 'a', encoding='utf-8') as f:
                        for item in data:
                            data2 = ast.literal_eval(str(item))
                            print("❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️")
                            f.write(f'{item}\n')
                else:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        data2 = ast.literal_eval(str(data)) 
                        print("❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️❤️")
                        f.write(f'{data}\n')

    except KeyboardInterrupt:
        consumer.close()

partition = 0  

# Lấy latest_offset
latest_offset = get_latest_offsets(bootstrap_servers, topic, partition)

start_offset = max(0, latest_offset - 1000)
end_offset = latest_offset

# Tệp tin đầu ra
output_file = 'output.txt'

consume_and_write_to_file(bootstrap_servers, topic, partition, start_offset, end_offset, output_file)