import pymongo
from statistics import mode
import math

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
        return "没有有效的评分数据"

    # 计算统计数据
    avg_score = sum(hotel_scores) / len(hotel_scores)
    median_score = sorted(hotel_scores)[len(hotel_scores) // 2]
    max_score = max(hotel_scores)
    min_score = min(hotel_scores)
    try:
        mode_score = mode(hotel_scores)
    except:
        mode_score = None  # 如果众数无法计算（数据不唯一），则为None

    return {
        "平均分": avg_score,
        "中位数": median_score,
        "最高分": max_score,
        "最低分": min_score,
        "众数": mode_score
    }


# 调用函数并打印结果
score_stats = get_hotel_score_statistics()
print("酒店评分统计:", score_stats)
