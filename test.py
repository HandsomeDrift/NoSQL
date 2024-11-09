import pymongo

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']

# 查询北京和天津的“高档型”酒店的经纬度信息
def query_beijing_tianjin_hotel_coordinates():
    hotels = hotel_info_collection.find(
        {"hotel_city_name": {"$in": ["北京", "天津"]}, "hotel_grade_text": "高档型"},
        {"hotel_name": 1, "hotel_city_name": 1, "hotel_location_info": 1, "latitude": 1, "longitude": 1}
    )

    # 输出结果
    for hotel in hotels:
        hotel_name = hotel.get("hotel_name", "未知酒店")
        city_name = hotel.get("hotel_city_name", "未知城市")
        location_info = hotel.get("hotel_location_info", "未知地址")
        latitude = hotel.get("latitude")
        longitude = hotel.get("longitude")

        print(f"酒店名称: {hotel_name}")
        print(f"城市: {city_name}")
        print(f"地址: {location_info}")
        if latitude and longitude:
            print(f"经纬度: 纬度 {latitude}, 经度 {longitude}")
        else:
            print("经纬度信息缺失")
        print("-" * 30)

# 调用查询函数
query_beijing_tianjin_hotel_coordinates()
