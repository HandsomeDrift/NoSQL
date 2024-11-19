import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient

# 设置 Matplotlib 字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用无衬线字体
plt.rcParams['axes.unicode_minus'] = False   # 解决负号显示问题

# MongoDB连接设置
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']
hotel_room_collection = db['hotel_room']

# 查询数据并按类型分类
def get_hotel_score_room_price_by_grade():
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
                "hotel_grade_text": 1,
                "hotel_score": 1,
                "max_room_price": {"$max": "$rooms.room_price"}
            }
        },
        {
            "$group": {
                "_id": "$hotel_grade_text",  # 按酒店类型分组
                "hotels": {
                    "$push": {
                        "hotel_name": "$hotel_name",
                        "hotel_score": "$hotel_score",
                        "max_room_price": "$max_room_price"
                    }
                }
            }
        }
    ]

    result = hotel_info_collection.aggregate(pipeline)

    hotel_data_by_grade = {}
    for entry in result:
        grade = entry["_id"]
        hotel_data_by_grade[grade] = entry["hotels"]

    return hotel_data_by_grade

# 绘制图表
def plot_hotel_score_vs_room_price_by_grade(hotel_data_by_grade):
    for grade, hotels in hotel_data_by_grade.items():
        if not hotels:
            print(f"Hotel grade '{grade}' has no data, skipping plot.")
            continue

        # 提取评分和价格，过滤掉 None 值
        scores = [hotel["hotel_score"] for hotel in hotels if hotel["hotel_score"] is not None and hotel["max_room_price"] is not None]
        prices = [hotel["max_room_price"] for hotel in hotels if hotel["hotel_score"] is not None and hotel["max_room_price"] is not None]

        if not scores or not prices:
            print(f"Hotel grade '{grade}' has insufficient data, cannot plot.")
            continue

        # 设置 Seaborn 风格
        sns.set(style="whitegrid")

        # 绘制散点图
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=scores, y=prices, hue=scores, palette="viridis", s=100, legend=False)

        # 设置标题和轴标签
        plt.title(f"Hotel Scores vs. Max Room Prices ({grade})", fontsize=16, fontproperties="SimSun")
        plt.xlabel("Hotel Score", fontsize=14)
        plt.ylabel("Max Room Price (CNY)", fontsize=14)

        # 添加网格
        plt.grid(visible=True, linestyle="--", alpha=0.6)

        # 显示图表
        plt.tight_layout()
        plt.show()

# 主程序
hotel_data_by_grade = get_hotel_score_room_price_by_grade()
plot_hotel_score_vs_room_price_by_grade(hotel_data_by_grade)
