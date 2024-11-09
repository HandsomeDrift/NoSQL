import pymongo
import pandas as pd
import folium
from folium.plugins import HeatMap

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']


# 查询北京和天津“高档型”酒店的经纬度
def get_beijing_tianjin_hotel_coordinates():
    hotels = hotel_info_collection.find(
        {"hotel_city_name": {"$in": ["北京", "天津"]}, "hotel_grade_text": "高档型"},
        {"latitude": 1, "longitude": 1, "hotel_city_name": 1}
    )

    coordinates = []
    for hotel in hotels:
        latitude = hotel.get("latitude")
        longitude = hotel.get("longitude")

        if latitude is not None and longitude is not None:
            coordinates.append([latitude, longitude])

    return coordinates


# 绘制热力图
def plot_heatmap(coordinates):
    # 设置地图中心和缩放级别
    m = folium.Map(location=[39.9042, 116.4074], zoom_start=10)  # 北京的中心坐标

    # 添加热力图层
    HeatMap(coordinates, radius=10, blur=15, max_zoom=12).add_to(m)

    # 保存热力图
    m.save("beijing_tianjin_hotel_heatmap.html")
    print("热力图已保存为 'beijing_tianjin_hotel_heatmap.html'")


# 获取酒店经纬度数据并绘制热力图
coordinates = get_beijing_tianjin_hotel_coordinates()
if coordinates:
    plot_heatmap(coordinates)
else:
    print("没有找到符合条件的酒店经纬度数据。")
