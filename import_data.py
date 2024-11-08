import pandas as pd
from pymongo import MongoClient

# MongoDB连接设置
client = MongoClient('mongodb://localhost:27017/')
db = client['hotel_database']

# 加载Excel文件
hotel_info_df = pd.read_excel('hotel_info.xlsx')
hotel_room_df = pd.read_excel('hotel_room.xlsx')

# 获取hotel_info和hotel_room集合
hotel_info_collection = db['hotel_info']
hotel_room_collection = db['hotel_room']

# 插入酒店信息（hotel_info）
for index, row in hotel_info_df.iterrows():
    hotel_data = {
        "hotel_name": row['hotel_name'],
        "hotel_id": row['hotel_id'],
        "hotel_score": row['hotel_score'],
        "hotel_image_id": row['hotel_image_id'],
        "hotel_location_info": row['hotel_location_info'],
        "hotel_grade_text": row['hotel_grade_text'],
        "hotel_comment_desc": row['hotel_comment_desc'],
        "hotel_city_name": row['hotel_city_name']
    }
    hotel_info_collection.insert_one(hotel_data)

# 插入酒店房间信息（hotel_room）
for index, row in hotel_room_df.iterrows():
    room_data = {
        "room_name": row['room_name'],
        "hotel_id": row['hotel_id'],  # 外键关联酒店
        "room_id": row['room_id'],
        "room_image_url": row['room_image_url'],
        "room_area": row['room_area'],
        "room_bed_type": row['room_bed_type'],
        "room_window": row['room_window'],
        "room_breakfast_num": row['room_breakfast_num'],
        "room_wifi": row['room_wifi'],
        "room_price": row['room_price'],
        "room_exist_num": row['room_exist_num']
    }
    hotel_room_collection.insert_one(room_data)

print("数据已成功导入MongoDB！")

