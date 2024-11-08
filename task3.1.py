import pymongo
import requests
import re
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
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
def get_coordinates_from_address(address):
    cleaned_address = clean_address(address)
    params = {
        'address': cleaned_address,
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


# 任务：展示北京和天津的“高档型”酒店的分布热力图
def plot_beijing_tianjin_hotel_heatmap():
    hotels = hotel_info_collection.find(
        {"hotel_location_info": {"$regex": "北京|天津"}, "hotel_grade_text": "高档型"},
        {"hotel_name": 1, "hotel_location_info": 1, "latitude": 1, "longitude": 1}
    )

    latitudes = []
    longitudes = []

    for hotel in hotels:
        hotel_id = hotel["_id"]
        latitude = hotel.get("latitude")
        longitude = hotel.get("longitude")

        # 如果经纬度不存在，调用API获取
        if latitude is None or longitude is None:
            location_info = hotel.get("hotel_location_info", "")
            latitude, longitude = get_coordinates_from_address(location_info)

            # 保存经纬度信息到数据库
            if latitude and longitude:
                save_coordinates_to_db(hotel_id, latitude, longitude)

        # 收集有效的经纬度数据
        if latitude and longitude:
            latitudes.append(latitude)
            longitudes.append(longitude)

        # 每次请求后延时1秒
        time.sleep(1)

    if not latitudes or not longitudes:
        print("没有有效的坐标数据")
        return

    # 加载北京和天津的地图数据
    china_map = gpd.read_file("ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp", engine="pyogrio")
    beijing_tianjin_map = china_map[(china_map['NAME'] == 'China')]

    # 创建绘图
    plt.figure(figsize=(8, 6))
    ax = beijing_tianjin_map.plot(color='lightgrey', edgecolor='black')

    # 绘制热力图
    sns.kdeplot(
        x=longitudes, y=latitudes,
        cmap="Reds", fill=True, alpha=0.5, ax=ax, bw_adjust=0.5
    )

    plt.title("北京和天津高档型酒店分布热力图")
    plt.xlabel("经度")
    plt.ylabel("纬度")
    plt.show()


# 调用函数绘制北京和天津的地图热力图
plot_beijing_tianjin_hotel_heatmap()
