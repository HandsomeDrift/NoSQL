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
