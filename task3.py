import pymongo
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']


# 任务3：展示北京和天津“高档型”酒店的分布热力图
def plot_hotel_distribution():
    # 获取北京和天津的高档型酒店
    hotels = hotel_info_collection.find({
        "hotel_city_name": {"$in": ["北京", "天津"]},
        "hotel_grade_text": "高档型"
    })

    # 生成酒店坐标点数据
    hotel_points = []
    for hotel in hotels:
        # 假设"hotel_location_info"字段包含坐标数据，如 "39.9042, 116.4074"
        coords = hotel["hotel_location_info"].split(',')
        latitude = float(coords[0].strip())
        longitude = float(coords[1].strip())
        hotel_points.append(Point(longitude, latitude))

    # 创建GeoDataFrame
    gdf = gpd.GeoDataFrame(geometry=hotel_points)

    # 画出热力图
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    ax = world.plot(figsize=(10, 10))
    gdf.plot(ax=ax, color='red', alpha=0.5, markersize=10)
    plt.title('北京和天津高档型酒店分布热力图')
    plt.show()


# 调用函数
plot_hotel_distribution()
