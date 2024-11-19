import pymongo
import matplotlib.pyplot as plt
import seaborn as sns

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']
hotel_room_collection = db['hotel_room']

# 为 hotel_id 和 room_price 字段创建索引（确保优化）
hotel_info_collection.create_index([("hotel_id", pymongo.ASCENDING)])
hotel_room_collection.create_index([("hotel_id", pymongo.ASCENDING), ("room_price", pymongo.DESCENDING)])


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
        if hotel["hotel_score"] is not None and hotel["max_room_price"] is not None:
            hotel_score_room_price.append({
                "酒店名称": hotel["hotel_name"],
                "评分": hotel["hotel_score"],
                "最贵房间价格": hotel["max_room_price"]
            })

    return hotel_score_room_price


# import matplotlib.pyplot as plt
# import seaborn as sns
from matplotlib import rcParams

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体显示中文
plt.rcParams['axes.unicode_minus'] = False   # 确保负号正常显示

# 任务2：展示酒店评分与房间价格的关系
def plot_hotel_score_vs_room_price(data):
    if not data:
        print("没有可用的数据进行绘图。")
        return

    # 转换为列表格式适合可视化
    scores = [item["评分"] for item in data]
    prices = [item["最贵房间价格"] for item in data]

    # 设置 Seaborn 风格
    sns.set(style="whitegrid")

    # 绘制散点图
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=scores, y=prices, hue=scores, palette="viridis", s=100, legend=False)

    # 设置标题和轴标签
    plt.title("Relationship between hotel ratings and the price of the most expensive room", fontsize=16)
    plt.xlabel("Hotel score", fontsize=14)
    plt.ylabel("Most expensive room price (yuan)", fontsize=14)

    # 添加网格
    plt.grid(visible=True, linestyle="--", alpha=0.6)

    # 显示图表
    plt.tight_layout()
    plt.show()


# 获取数据
hotel_room_price_stats = get_hotel_score_room_price_relationship_optimized()

# 绘制图表
plot_hotel_score_vs_room_price(hotel_room_price_stats)
