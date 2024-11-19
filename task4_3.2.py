import pymongo
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

# 设置 matplotlib 字体支持中文
plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用 SimHei 显示中文
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题

# MongoDB 连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']

# 查询数据：聚合分析评论和评分
def analyze_comment_sentiments():
    pipeline = [
        {
            "$group": {
                "_id": "$hotel_comment_desc",
                "average_score": {"$avg": "$hotel_score"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"count": -1}}  # 按评论数量排序
    ]

    result = hotel_info_collection.aggregate(pipeline)
    sentiment_data = []

    # 清洗数据：将空值或空字符串处理为“未评价”
    for entry in result:
        comment = entry["_id"]
        if not isinstance(comment, str) or comment.strip() == "":
            comment = "未评价"
        sentiment_data.append({
            "comment": comment,
            "average_score": entry["average_score"],
            "count": entry["count"]
        })

    return sentiment_data


# 绘制图表：柱状图 + 趋势图
def plot_sentiment_analysis(sentiment_data):
    comments = [entry["comment"] for entry in sentiment_data]
    counts = [entry["count"] for entry in sentiment_data]
    avg_scores = [entry["average_score"] for entry in sentiment_data]

    # 中文字符处理：限制显示的评论数量
    max_comments = 15  # 最多显示前15条评论
    comments = comments[:max_comments]
    counts = counts[:max_comments]
    avg_scores = avg_scores[:max_comments]

    sns.set(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 柱状图 - 评论数量
    ax1.bar(range(len(comments)), counts, color='skyblue', label='评论数')
    ax1.set_xlabel("评论内容索引", fontsize=14)
    ax1.set_ylabel("评论数量", fontsize=14, color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # 将索引对应到评论内容
    plt.xticks(range(len(comments)), comments, rotation=45, fontsize=10)

    # 折线图 - 平均评分
    ax2 = ax1.twinx()
    ax2.plot(range(len(comments)), avg_scores, color='orange', marker='o', label='平均评分')
    ax2.set_ylabel("平均评分", fontsize=14, color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # 添加标题和图例
    plt.title("评论内容与评分统计分析", fontsize=16)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    # 自动调整布局
    plt.tight_layout()
    plt.show()


# 主程序
sentiment_data = analyze_comment_sentiments()
plot_sentiment_analysis(sentiment_data)
