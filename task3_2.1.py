import json
import pymongo
from folium import Map
from folium.plugins import HeatMap

# MongoDB连接
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']

# 查询酒店数据并导出为 JSON
def export_hotel_coordinates():
    hotels = hotel_info_collection.find(
        {"hotel_city_name": {"$in": ["北京", "天津"]}, "hotel_grade_text": "高档型"},
        {"latitude": 1, "longitude": 1, "hotel_name": 1, "hotel_city_name": 1}
    )

    data = []
    for hotel in hotels:
        if hotel.get("latitude") and hotel.get("longitude"):
            data.append({
                "name": hotel.get("hotel_name", "未知"),
                "city": hotel.get("hotel_city_name", "未知"),
                "lat": hotel["latitude"],
                "lng": hotel["longitude"]
            })

    # 导出为 JSON 文件
    with open("hotel_coordinates.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("酒店数据已导出为 hotel_coordinates.json")

# 生成基础 HTML
def generate_heatmap_base():
    # 初始化地图
    m = Map(location=[39.9042, 116.4074], zoom_start=10)

    # 保存基础 HTML
    m.save("heatmap.html")
    print("基础地图已保存为 heatmap.html")

# 执行导出和生成
export_hotel_coordinates()
generate_heatmap_base()
