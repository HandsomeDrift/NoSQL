import pymongo
from statistics import mode
import math
import matplotlib.pyplot as plt
import seaborn as sns

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']

# 任务1：展示酒店评分的平均分、中位数、最高分、最低分、众数
def get_hotel_score_statistics():
    # 获取所有有效酒店评分数据（排除空值、NaN和非数字值）
    hotel_scores = []
    for doc in hotel_info_collection.find({}, {'hotel_score': 1}):
        score = doc.get('hotel_score', None)
        # 只处理有效的评分数据（非空、非NaN、且是数字类型）
        if score is not None and isinstance(score, (int, float)) and not math.isnan(score):
            hotel_scores.append(score)

    if not hotel_scores:
        return "No valid score data found.", []

    # 计算统计数据
    avg_score = sum(hotel_scores) / len(hotel_scores)
    median_score = sorted(hotel_scores)[len(hotel_scores) // 2]
    max_score = max(hotel_scores)
    min_score = min(hotel_scores)
    try:
        mode_score = mode(hotel_scores)
    except:
        mode_score = None  # 如果众数无法计算（数据不唯一），则为None

    statistics = {
        "Average": avg_score,
        "Median": median_score,
        "Maximum": max_score,
        "Minimum": min_score,
        "Mode": mode_score
    }
    return statistics, hotel_scores


# 可视化评分数据
def visualize_hotel_scores(hotel_scores, stats):
    sns.set(style="whitegrid")

    # 直方图
    plt.figure(figsize=(12, 6))
    sns.histplot(hotel_scores, bins=20, kde=True, color="skyblue", edgecolor="black")
    plt.axvline(stats["Average"], color="orange", linestyle="--", label=f"Average: {stats['Average']:.2f}")
    plt.axvline(stats["Median"], color="green", linestyle="--", label=f"Median: {stats['Median']:.2f}")
    plt.axvline(stats["Maximum"], color="red", linestyle="--", label=f"Maximum: {stats['Maximum']:.2f}")
    plt.axvline(stats["Minimum"], color="blue", linestyle="--", label=f"Minimum: {stats['Minimum']:.2f}")
    if stats["Mode"] is not None:
        plt.axvline(stats["Mode"], color="purple", linestyle="--", label=f"Mode: {stats['Mode']:.2f}")
    plt.title("Hotel Score Distribution - Histogram", fontsize=16)
    plt.xlabel("Score", fontsize=14)
    plt.ylabel("Frequency", fontsize=14)
    plt.legend(fontsize=12)
    plt.show()

    # 箱线图
    plt.figure(figsize=(8, 6))
    sns.boxplot(x=hotel_scores, color="lightblue")
    plt.axvline(stats["Average"], color="orange", linestyle="--", label="Average")
    plt.axvline(stats["Median"], color="green", linestyle="--", label="Median")
    plt.title("Hotel Score Distribution - Boxplot", fontsize=16)
    plt.xlabel("Score", fontsize=14)
    plt.legend(fontsize=12)
    plt.show()


# 调用函数
score_stats, hotel_scores = get_hotel_score_statistics()
if isinstance(score_stats, str):
    print(score_stats)
else:
    print("Hotel Score Statistics:", score_stats)
    visualize_hotel_scores(hotel_scores, score_stats)
