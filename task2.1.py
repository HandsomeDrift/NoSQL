import pymongo
import csv

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']
hotel_room_collection = db['hotel_room']

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!重要
# # 为 hotel_id 和 room_price 字段创建索引
# hotel_info_collection.create_index([("hotel_id", pymongo.ASCENDING)])
# hotel_room_collection.create_index([("hotel_id", pymongo.ASCENDING), ("room_price", pymongo.DESCENDING)])



# 任务2：展示酒店评分与房间价格的关系，按酒店评分和房间价格的最贵房间进行统计
def get_hotel_score_room_price_relationship_optimized():
    pipeline = [
        {
            "$lookup": {
                "from": "hotel_room",
                "localField": "hotel_id",
                "foreignField": "hotel_id",
                "as": "rooms"
            }
        },
        {
            "$project": {
                "hotel_name": 1,
                "hotel_score": 1,
                "max_room_price": {
                    "$max": "$rooms.room_price"
                }
            }
        },
        {
            "$sort": {
                "hotel_score": -1
            }
        }
    ]

    result = hotel_info_collection.aggregate(pipeline)

    hotel_score_room_price = []
    for hotel in result:
        hotel_score_room_price.append({
            "酒店名称": hotel["hotel_name"],
            "评分": hotel["hotel_score"],
            "最贵房间价格": hotel["max_room_price"]
        })

    return hotel_score_room_price


# 将结果写入 CSV 文件
def write_to_csv(data, filename="hotel_score_room_price.csv"):
    keys = data[0].keys()  # 获取字典的键作为CSV的列名

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"结果已保存到 {filename}")


# 获取数据并保存到文件
hotel_room_price_stats = get_hotel_score_room_price_relationship_optimized()
write_to_csv(hotel_room_price_stats)
