from elasticsearch import Elasticsearch
from datetime import datetime

def get_link_es(gte,lte):
    # load_dotenv()
    # es_address = os.getenv("Elasticsearch")
    es = Elasticsearch(["http://172.168.200.202:9200"])
    body = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"type.keyword": "tiktok video"}},
                    {
                        "range": {
                            "created_time": {
                                "gte": gte,
                                "lte": lte,
                                "format": "MM/dd/yyyy HH:mm:ss"
                            }
                        }
                    }
                ]
            }
        },
        "size": 10000,
        "sort": [
            {
                "created_time": {
                    "order": "asc"
                }
            }
        ],
        "_source": ["link"]
    }
    
    result = es.search(index="posts", body=body)
    links=[]
    for hit in result['hits']['hits']:
        links.append(hit['_source']['link'])
    es.close()
    return links
    
        
# if __name__ == "__main__":
#     type_list=['tiktok video']
#     # format : mm/dd/yyyy hh:mm:ss
#     gte='02/19/2024 10:00:00'
#     lte='02/20/2024 10:00:00'
#     link = get_link_es(gte,lte)
#     print(link)