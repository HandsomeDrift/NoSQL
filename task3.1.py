import pymongo
import requests
import re
import time

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']

# 百度地图API地址解析服务
BAIDU_MAP_API_KEY = "vPZMuhEdII6H5BjQsR5zmMR7tiTa5eCA"  # 请替换为你从百度地图开发者平台获得的API密钥
BAIDU_MAP_GEOCODING_URL = "http://api.map.baidu.com/geocoding/v3/"


# 清理地址中的特殊字符
def clean_address(address):
    cleaned_address = re.sub(r"\s*·\s*|/", "", address)
    return cleaned_address


# 地理编码函数：通过百度地图API获取经纬度
def get_coordinates_from_address(city, address):
    full_address = f"{city}{clean_address(address)}"
    params = {
        'address': full_address,
        'output': 'json',
        'ak': BAIDU_MAP_API_KEY
    }

    response = requests.get(BAIDU_MAP_GEOCODING_URL, params=params)

    if response.status_code == 200:
        result = response.json()
        if result.get("status") == 0:
            lat = result["result"]["location"]["lat"]
            lng = result["result"]["location"]["lng"]
            return lat, lng
    return None, None


# 更新MongoDB文档，保存经纬度信息
def save_coordinates_to_db(hotel_id, latitude, longitude):
    hotel_info_collection.update_one(
        {"_id": hotel_id},
        {"$set": {"latitude": latitude, "longitude": longitude}}
    )


# 任务：重新查询北京和天津的“高档型”酒店的经纬度并保存到数据库中
def update_beijing_tianjin_hotel_coordinates():
    hotels = hotel_info_collection.find(
        {"hotel_city_name": {"$in": ["北京", "天津"]}, "hotel_grade_text": "高档型"},
        {"hotel_city_name": 1, "hotel_location_info": 1}
    )

    for hotel in hotels:
        hotel_id = hotel["_id"]
        city_name = hotel.get("hotel_city_name", "")
        location_info = hotel.get("hotel_location_info", "")

        # 查询经纬度
        latitude, longitude = get_coordinates_from_address(city_name, location_info)

        # 保存经纬度信息到数据库
        if latitude and longitude:
            save_coordinates_to_db(hotel_id, latitude, longitude)
            print(f"酒店ID {hotel_id} 的经纬度已更新：纬度 {latitude}, 经度 {longitude}")
        else:
            print(f"无法获取酒店ID {hotel_id} 的经纬度")

        # 每次请求后延时1秒，避免过多请求
        time.sleep(1)


# 调用函数更新经纬度
update_beijing_tianjin_hotel_coordinates()
