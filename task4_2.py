import pymongo
import matplotlib.pyplot as plt

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_room_collection = db['hotel_room']
hotel_info_collection = db['hotel_info']


def analyze_price_distribution_by_hotel_grade():
    # 聚合查询每种类型的酒店及其房间价格
    pipeline = [
        {"$lookup": {
            "from": "hotel_info",
            "localField": "hotel_id",
            "foreignField": "hotel_id",
            "as": "hotel_info"
        }},
        {"$unwind": "$hotel_info"},
        {"$group": {
            "_id": "$hotel_info.hotel_grade_text",
            "prices": {"$push": "$room_price"}
        }},
        {"$sort": {"_id": 1}}  # 按照酒店类型排序
    ]

    price_data = list(hotel_room_collection.aggregate(pipeline))

    hotel_types = []
    price_lists = []

    for item in price_data:
        hotel_type = item["_id"]
        prices = [price for price in item["prices"] if price is not None]

        hotel_types.append(hotel_type)
        price_lists.append(prices)

    # 绘制箱线图
    plt.figure(figsize=(10, 6))
    plt.boxplot(price_lists, labels=hotel_types, vert=True, patch_artist=True)
    plt.title("不同酒店类型的房间价格分布")
    plt.xlabel("酒店类型")
    plt.ylabel("房间价格")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()


# 调用分析函数
analyze_price_distribution_by_hotel_grade()
