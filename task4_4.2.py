from geopy.distance import geodesic
import matplotlib.pyplot as plt
import networkx as nx
from pymongo import MongoClient
from itertools import combinations

# MongoDB连接设置
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']
hotel_info_collection = db['hotel_info']

# 查询酒店地理信息
def fetch_beijing_tianjin_hotels():
    query = {
        "hotel_city_name": {"$in": ["北京", "天津"]},
        "latitude": {"$exists": True},
        "longitude": {"$exists": True}
    }
    projection = {
        "hotel_name": 1,
        "hotel_city_name": 1,
        "latitude": 1,
        "longitude": 1
    }
    return list(hotel_info_collection.find(query, projection))

# 计算距离矩阵
def calculate_distance_matrix(hotels):
    distances = []
    hotel_pairs = []

    for hotel1, hotel2 in combinations(hotels, 2):
        loc1 = (hotel1["latitude"], hotel1["longitude"])
        loc2 = (hotel2["latitude"], hotel2["longitude"])

        # 计算两点之间的地理距离
        dist = geodesic(loc1, loc2).kilometers
        distances.append(dist)
        hotel_pairs.append((hotel1, hotel2, dist))

    return hotel_pairs, distances

# 可视化距离分布
def plot_hotel_distances(hotel_pairs, distances):
    # 距离分布
    plt.figure(figsize=(12, 8))
    plt.hist(distances, bins=15, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title("Hotel Distance Distribution", fontsize=16)
    plt.xlabel("Distance (km)", fontsize=14)
    plt.ylabel("Count", fontsize=14)
    plt.grid(alpha=0.5)
    plt.tight_layout()
    plt.show()

    # 最近和最远的酒店对
    min_distance_pair = min(hotel_pairs, key=lambda x: x[2])
    max_distance_pair = max(hotel_pairs, key=lambda x: x[2])

    print("=== Closest Hotels ===")
    print(f"Hotel 1: {min_distance_pair[0]['hotel_name']} (City: {min_distance_pair[0]['hotel_city_name']})")
    print(f"Hotel 2: {min_distance_pair[1]['hotel_name']} (City: {min_distance_pair[1]['hotel_city_name']})")
    print(f"Distance: {min_distance_pair[2]:.2f} km\n")

    print("=== Farthest Hotels ===")
    print(f"Hotel 1: {max_distance_pair[0]['hotel_name']} (City: {max_distance_pair[0]['hotel_city_name']})")
    print(f"Hotel 2: {max_distance_pair[1]['hotel_name']} (City: {max_distance_pair[1]['hotel_city_name']})")
    print(f"Distance: {max_distance_pair[2]:.2f} km\n")

    # 创建图
    G = nx.Graph()
    for hotel1, hotel2, dist in hotel_pairs:
        if dist < 3:  # 仅保留距离小于10km的边
            G.add_edge(hotel1["hotel_name"], hotel2["hotel_name"], weight=dist)

    # 使用布局算法
    pos = nx.spring_layout(G, seed=42, k=5.0)  # 调整 k 值增大节点间距

    # 增加画布大小
    plt.figure(figsize=(100, 80))
    nx.draw(
        G, pos, with_labels=False, node_size=1500, node_color="lightblue",
        edge_color="gray", font_size=10, font_weight="bold"
    )

    # 显示序列号标签
    hotel_names = list(G.nodes)
    node_labels = {node: f"Hotel-{i}" for i, node in enumerate(hotel_names)}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=12)

    # 仅标注短边的距离
    edge_labels = {(u, v): f"{d['weight']:.1f} km" for u, v, d in G.edges(data=True) if d['weight'] < 5}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

    # 图标题
    plt.title("Hotel Distance Network (Distances < 10 km)", fontsize=18)
    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
    plt.show()

    # 打印序列号与酒店名称映射
    print("=== Hotel Name Mapping ===")
    for i, name in enumerate(hotel_names):
        print(f"Hotel-{i}: {name}")

# 主程序
hotels = fetch_beijing_tianjin_hotels()
if not hotels:
    print("No hotel data found in the database.")
else:
    hotel_pairs, distances = calculate_distance_matrix(hotels)
    if distances:
        plot_hotel_distances(hotel_pairs, distances)
    else:
        print("No valid distance data available.")
