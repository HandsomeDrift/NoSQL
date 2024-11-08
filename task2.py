import pymongo

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']
hotel_room_collection = db['hotel_room']


# 任务2：展示酒店评分与房间价格的关系
def get_hotel_score_room_price_relationship():
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
                "max_room_price": {"$max": "$rooms.room_price"}
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


# 调用函数并打印结果
hotel_room_price_stats = get_hotel_score_room_price_relationship()
print("酒店评分与房间价格的关系:")
for entry in hotel_room_price_stats:
    print(entry)
