import pymongo
import matplotlib.pyplot as plt

# 设置 Matplotlib 字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用无衬线字体
plt.rcParams['axes.unicode_minus'] = False   # 解决负号显示问题

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

    for item in price_data:
        hotel_type = item["_id"]
        prices = [price for price in item["prices"] if price is not None]

        # 每个类别单独绘制盒线图
        plt.figure(figsize=(8, 5))
        plt.boxplot(prices, vert=True, patch_artist=True)
        plt.title(f"{hotel_type}的房间价格分布", fontproperties="SimSun")
        plt.xlabel("房间类型", fontproperties="SimSun")
        plt.ylabel("房间价格", fontproperties="SimSun")
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.show()


# 调用分析函数
analyze_price_distribution_by_hotel_grade()
