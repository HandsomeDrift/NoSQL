import pymongo
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']


# 任务：展示北京和天津的“高档型”酒店的分布热力图
def plot_beijing_tianjin_hotel_heatmap():
    hotels = hotel_info_collection.find(
        {"hotel_location_info": {"$regex": "北京|天津"}, "hotel_grade_text": "高档型"},
        {"latitude": 1, "longitude": 1}
    )

    # 收集经纬度数据
    latitudes = [hotel["latitude"] for hotel in hotels if hotel.get("latitude") and hotel.get("longitude")]
    longitudes = [hotel["longitude"] for hotel in hotels if hotel.get("latitude") and hotel.get("longitude")]

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
