from flask import Flask, request, jsonify, render_template
from geopy.distance import geodesic
import networkx as nx
from pymongo import MongoClient
from itertools import combinations

app = Flask(__name__)

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
    hotel_pairs = []
    for hotel1, hotel2 in combinations(hotels, 2):
        loc1 = (hotel1["latitude"], hotel1["longitude"])
        loc2 = (hotel2["latitude"], hotel2["longitude"])
        dist = geodesic(loc1, loc2).kilometers
        hotel_pairs.append((hotel1, hotel2, dist))
    return hotel_pairs

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_network', methods=['POST'])
def get_network():
    distance_threshold = float(request.form.get('distance_threshold', 10))  # 用户设定的距离
    hotels = fetch_beijing_tianjin_hotels()
    hotel_pairs = calculate_distance_matrix(hotels)

    # 过滤距离小于阈值的边
    filtered_edges = [
        {
            "source": hotel1["hotel_name"],
            "target": hotel2["hotel_name"],
            "distance": dist
        }
        for hotel1, hotel2, dist in hotel_pairs if dist < distance_threshold
    ]

    nodes = [{"id": hotel["hotel_name"], "city": hotel["hotel_city_name"]} for hotel in hotels]
    return jsonify({"nodes": nodes, "edges": filtered_edges})

if __name__ == '__main__':
    app.run(debug=True)
