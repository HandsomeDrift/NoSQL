# NoSQL课程实验

## 数据集分析

### hotel_info

id：酒店序列编号，从1开始递增

hotel_name：酒店名称

hotel_id：酒店编号

hotel_score：酒店评分

hotel_img_id：酒店照片网址

hotel_location_info：酒店地址

hotel_grade_text：酒店类型，例如高档型、豪华型、经济型等

hotel_comment_desc：酒店评价，例如棒、超棒、不错、好、很好等

hotel_city_name：酒店所在城市名称

### hotel_room

room_name：酒店房间名称

hotel_id：房间所属的酒店编号

room_id：房间编号

room_image_url：房间照片URL

room_area：房间面积

room_bed_type：房间中床的尺寸和数量

room_window：是否有窗户

room_breakfast_num：是否提供早餐

room_wifi：是否有wifi

room_price：房间价格

room_exist_num：可以容纳的住户人数

id：房间序列编号，从1开始递增





### 任务四（1）：统计每个城市中最热门酒店的详细信息，并按评论分布统计其受欢迎的具体因素

**任务描述**：

1. 在每个城市中，通过`hotel_score`选择最热门的酒店，并提取该酒店的详细信息。
2. 对每个最热门酒店的评论字段`hotel_comment_desc`进行分词（可以用中文分词库如 `jieba`），统计词频以分析受欢迎的具体因素，并展示前5个高频关键词。

**目标**：
- 通过聚合操作和复杂文本分析展示城市内酒店的“热门度”。
- 在文本分析上运用分词等技术，深入解读酒店评价信息，从而展现数据库中结构化数据和非结构化数据的混合分析能力。

**实现代码**：

```python
import pymongo
from collections import Counter
import jieba  # 中文分词库
import re

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']

def analyze_top_hotels_in_cities():
    # 聚合查询每个城市评分最高的酒店
    pipeline = [
        {"$group": {
            "_id": "$hotel_city_name",
            "max_score": {"$max": "$hotel_score"}
        }},
        {"$lookup": {
            "from": "hotel_info",
            "localField": "_id",
            "foreignField": "hotel_city_name",
            "as": "city_hotels"
        }},
        {"$unwind": "$city_hotels"},
        {"$match": {"$expr": {"$eq": ["$max_score", "$city_hotels.hotel_score"]}}},
        {"$project": {
            "city_name": "$_id",
            "hotel_name": "$city_hotels.hotel_name",
            "hotel_score": "$max_score",
            "hotel_comment_desc": "$city_hotels.hotel_comment_desc"
        }}
    ]
    
    top_hotels = hotel_info_collection.aggregate(pipeline)
    
    for hotel in top_hotels:
        city = hotel['city_name']
        name = hotel['hotel_name']
        score = hotel['hotel_score']
        comment_desc = hotel['hotel_comment_desc']
        
        print(f"\n城市：{city}，最热门酒店：{name}，评分：{score}")
        
        # 使用jieba对评论分词并统计词频
        words = jieba.cut(comment_desc)
        word_counts = Counter([word for word in words if len(word) > 1])  # 去掉单个字符词
        
        # 展示前5个高频关键词
        print("受欢迎关键词：")
        for word, freq in word_counts.most_common(5):
            print(f"{word}: {freq}")

# 调用分析函数
analyze_top_hotels_in_cities()
```

**代码解析**：
1. **分组与最大评分匹配**：使用`$group`操作找到每个城市评分最高的酒店，然后通过`$lookup`和`$unwind`操作关联完整的酒店信息。
2. **分词与词频统计**：使用`jieba`库对评论分词，过滤掉无意义的单字符词语。统计词频，以分析评论中最常提及的关键词，展示前5个高频关键词。
3. **结果展示**：输出每个城市中最热门的酒店及其评论关键词，从而发现用户对这些酒店的喜爱点。


### 任务四（2）：分析不同酒店类型的房间价格分布，并绘制箱线图来展示价格的集中趋势和离散程度

**任务描述**：
1. 对不同`hotel_grade_text`（酒店类型）下的`room_price`进行分布统计，使用箱线图来分析每种酒店类型中房间价格的集中趋势、离散程度以及潜在的异常值。
2. 利用 MongoDB 聚合管道对不同类型的房间价格进行分组、统计，并将数据导出至 `matplotlib` 中进行可视化。

**目标**：
- 展示不同酒店类型的价格结构，识别高档、豪华、经济型酒店的价格分布特点。
- 展现数据聚合和统计分析与数据可视化的结合应用。

**实现代码**：

```python
import pymongo
import matplotlib.pyplot as plt

# MongoDB连接设置
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_room_collection = db['hotel_room']
hotel_info_collection = db['hotel_info']

def analyze_price_distribution_by_hotel_grade():
    # 聚合查询每种类型的酒店及其房间价格
    pipeline = [
        {"$lookup": {
            "from": "hotel_info",
            "localField": "hotel_id",
            "foreignField": "hotel_id",
            "as": "hotel_info"
        }},
        {"$unwind": "$hotel_info"},
        {"$group": {
            "_id": "$hotel_info.hotel_grade_text",
            "prices": {"$push": "$room_price"}
        }},
        {"$sort": {"_id": 1}}  # 按照酒店类型排序
    ]
    
    price_data = list(hotel_room_collection.aggregate(pipeline))
    
    hotel_types = []
    price_lists = []

    for item in price_data:
        hotel_type = item["_id"]
        prices = [price for price in item["prices"] if price is not None]
        
        hotel_types.append(hotel_type)
        price_lists.append(prices)

    # 绘制箱线图
    plt.figure(figsize=(10, 6))
    plt.boxplot(price_lists, labels=hotel_types, vert=True, patch_artist=True)
    plt.title("不同酒店类型的房间价格分布")
    plt.xlabel("酒店类型")
    plt.ylabel("房间价格")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.show()

# 调用分析函数
analyze_price_distribution_by_hotel_grade()
```

**代码解析**：
1. **数据聚合**：通过`$lookup`联表查询，将`hotel_room`集合与`hotel_info`集合关联，以获得每种酒店类型对应的房间价格列表。
2. **过滤空值并汇总**：过滤掉价格为空的数据，将每种酒店类型及其价格数据存储到两个列表中。
3. **箱线图绘制**：利用`matplotlib`绘制箱线图，展示每种酒店类型的房间价格分布。箱线图能够很好地展示价格的集中趋势和离散程度，并识别出潜在的异常值。

**任务效果**：
- 该任务通过箱线图直观展示不同酒店类型的房间价格分布，便于观察价格结构差异。
- 通过分析价格的集中趋势、离散程度和异常值，可以帮助了解高档、豪华、经济型酒店的不同价格策略和市场定位。





以下是任务四的两个高难度新任务设计，旨在展示数据库操作的深度与华丽的结果展示：

---

### **任务 4.1：动态分析评分和评论的情感倾向**
#### 目标：
1. 基于酒店的 `hotel_comment_desc`（例如 "棒", "超棒", "不错", "好", "很好" 等），利用 MongoDB 聚合管道动态分析各类型评论的分布。
2. 结合评分 `hotel_score` 统计出每种评论的平均评分。
3. 使用分布柱状图和平均评分线性趋势图动态展示结果。

#### 实现：
```python
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient

# MongoDB连接设置
client = MongoClient('mongodb://localhost:27017/')
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
    sentiment_data = list(result)

    return sentiment_data

# 绘制图表：柱状图 + 趋势图
def plot_sentiment_analysis(sentiment_data):
    comments = [entry["_id"] for entry in sentiment_data if entry["_id"] is not None]
    counts = [entry["count"] for entry in sentiment_data if entry["_id"] is not None]
    avg_scores = [entry["average_score"] for entry in sentiment_data if entry["_id"] is not None]

    sns.set(style="whitegrid")
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # 柱状图 - 评论数量
    ax1.bar(comments, counts, color='skyblue', label='Comment Count')
    ax1.set_xlabel("Comments", fontsize=14)
    ax1.set_ylabel("Comment Count", fontsize=14, color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    plt.xticks(rotation=45)

    # 折线图 - 平均评分
    ax2 = ax1.twinx()
    ax2.plot(comments, avg_scores, color='orange', marker='o', label='Average Score')
    ax2.set_ylabel("Average Score", fontsize=14, color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # 添加标题和图例
    plt.title("Comment Sentiments vs. Average Scores", fontsize=16)
    ax1.legend(loc='upper left')
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.show()

# 主程序
sentiment_data = analyze_comment_sentiments()
plot_sentiment_analysis(sentiment_data)
```

#### 亮点：
1. 使用 MongoDB 聚合管道实现动态评论分类分析，展示评论和评分的关系。
2. 图表动态展现每种评论的数量及其平均评分，通过双 Y 轴柱状图和折线图结合更直观。

---

### **任务 4.2：基于地理分布的距离分析与可视化**
#### 目标：
1. 对北京和天津的酒店，计算任意两两之间的距离，并找到距离最近和最远的酒店对。
2. 使用 GeoJSON 查询和 Python 绘制可视化，动态展示酒店的距离分布。

#### 实现：
```python
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import networkx as nx
from pymongo import MongoClient

# MongoDB连接设置
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']

# 查询酒店地理信息
def fetch_beijing_tianjin_hotels():
    query = {
        "hotel_city_name": {"$in": ["北京", "天津"]},
        "location": {"$exists": True}
    }
    projection = {"hotel_name": 1, "location": 1}
    return list(hotel_info_collection.find(query, projection))

# 计算距离矩阵
def calculate_distance_matrix(hotels):
    distances = []
    hotel_pairs = []

    for i, hotel1 in enumerate(hotels):
        for j, hotel2 in enumerate(hotels):
            if i >= j:  # 避免重复计算
                continue

            loc1 = hotel1["location"]["coordinates"]
            loc2 = hotel2["location"]["coordinates"]

            dist = geodesic((loc1[1], loc1[0]), (loc2[1], loc2[0])).kilometers
            distances.append(dist)
            hotel_pairs.append((hotel1["hotel_name"], hotel2["hotel_name"], dist))

    return hotel_pairs, distances

# 可视化距离分布
def plot_hotel_distances(hotel_pairs, distances):
    # 距离分布
    plt.figure(figsize=(10, 6))
    plt.hist(distances, bins=20, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title("Hotel Distance Distribution", fontsize=16)
    plt.xlabel("Distance (km)", fontsize=14)
    plt.ylabel("Count", fontsize=14)
    plt.grid(alpha=0.5)
    plt.show()

    # 最近和最远的酒店对
    min_distance_pair = min(hotel_pairs, key=lambda x: x[2])
    max_distance_pair = max(hotel_pairs, key=lambda x: x[2])

    print(f"Closest Hotels: {min_distance_pair[0]} and {min_distance_pair[1]}, Distance: {min_distance_pair[2]:.2f} km")
    print(f"Farthest Hotels: {max_distance_pair[0]} and {max_distance_pair[1]}, Distance: {max_distance_pair[2]:.2f} km")

    # 绘制网络图
    G = nx.Graph()
    for hotel1, hotel2, dist in hotel_pairs:
        if dist < 10:  # 只绘制小于10km的关系
            G.add_edge(hotel1, hotel2, weight=dist)

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=700, node_color="lightblue", font_size=10, font_weight="bold", edge_color="gray")
    plt.title("Hotel Distance Network (Distances < 10 km)", fontsize=16)
    plt.show()

# 主程序
hotels = fetch_beijing_tianjin_hotels()
hotel_pairs, distances = calculate_distance_matrix(hotels)
plot_hotel_distances(hotel_pairs, distances)
```

#### 亮点：
1. 使用 Geopy 计算酒店之间的真实地理距离，展示最近和最远的酒店对。
2. 结合 NetworkX 绘制酒店的地理距离网络图，展示地理分布关系。
3. 距离分布的直方图直观呈现数据分布特征。

---

通过以上两个任务，展示了在 MongoDB 中深度查询、分析和可视化数据的能力。