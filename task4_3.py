import pymongo
import matplotlib.pyplot as plt
import seaborn as sns

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

    # 清洗数据：将空值、非字符串类型或空字符串处理为“未评价”
    for entry in result:
        comment = entry["_id"]
        if not isinstance(comment, str) or not comment.strip():
            comment = "未评价"
        sentiment_data.append({
            "comment": comment,
            "average_score": entry["average_score"],
            "count": entry["count"]
        })

    return sentiment_data


# 绘制图表
def plot_sentiment_analysis(sentiment_data):
    # 提取数据并准备映射表
    comments = [data["comment"] for data in sentiment_data]
    counts = [data["count"] for data in sentiment_data]
    scores = [data["average_score"] for data in sentiment_data]
    comment_to_index = {comment: idx for idx, comment in enumerate(comments)}

    # 创建一个新的 x 轴标签：编号
    indices = list(comment_to_index.values())

    # 设置画布
    sns.set(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 柱状图：评论数量
    ax1.bar(indices, counts, color='skyblue', label='Comment Count')
    ax1.set_xlabel("Comment Index")
    ax1.set_ylabel("Number of Comments", color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_xticks(indices)
    ax1.set_xticklabels(indices, rotation=45, fontsize=10)

    # 折线图：平均评分
    ax2 = ax1.twinx()
    ax2.plot(indices, scores, color='orange', label='Average Score', marker='o')
    ax2.set_ylabel("Average Score", color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # 添加标题和图例
    plt.title("Sentiment Analysis of Hotel Comments", fontsize=16)
    fig.tight_layout()
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")

    # 显示图表
    plt.show()

    # 打印评论编号映射
    print("Comment Index Mapping:")
    for idx, comment in enumerate(comments):
        print(f"{idx}: {comment}")


# 主程序：运行分析和绘图
sentiment_data = analyze_comment_sentiments()
plot_sentiment_analysis(sentiment_data)
