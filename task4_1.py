import pymongo
from collections import Counter
import jieba  # 中文分词库
import re

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']


def analyze_top_hotels_in_cities():
    # 聚合查询每个城市评分最高的酒店
    pipeline = [
        {"$group": {
            "_id": "$hotel_city_name",
            "max_score": {"$max": "$hotel_score"}
        }},
        {"$lookup": {
            "from": "hotel_info",
            "localField": "_id",
            "foreignField": "hotel_city_name",
            "as": "city_hotels"
        }},
        {"$unwind": "$city_hotels"},
        {"$match": {"$expr": {"$eq": ["$max_score", "$city_hotels.hotel_score"]}}},
        {"$project": {
            "city_name": "$_id",
            "hotel_name": "$city_hotels.hotel_name",
            "hotel_score": "$max_score",
            "hotel_comment_desc": "$city_hotels.hotel_comment_desc"
        }}
    ]

    top_hotels = hotel_info_collection.aggregate(pipeline)

    for hotel in top_hotels:
        city = hotel['city_name']
        name = hotel['hotel_name']
        score = hotel['hotel_score']
        comment_desc = hotel['hotel_comment_desc']

        print(f"\n城市：{city}，最热门酒店：{name}，评分：{score}")

        # 使用jieba对评论分词并统计词频
        words = jieba.cut(comment_desc)
        word_counts = Counter([word for word in words if len(word) > 1])  # 去掉单个字符词

        # 展示前5个高频关键词
        print("受欢迎关键词：")
        for word, freq in word_counts.most_common(5):
            print(f"{word}: {freq}")


# 调用分析函数
analyze_top_hotels_in_cities()
