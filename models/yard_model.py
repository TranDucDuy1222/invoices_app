from .base_model import BaseModel
from tkinter import messagebox
import sqlite3


class YardModel(BaseModel):
    def __init__(self, db_path):
        # Gọi __init__ của lớp cha (BaseModel) để có self.conn và self.cursor
        super().__init__(db_path)

    def get_vehicle(self):
        query = "select id_car, bien_so from cars"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi truy vấn dữ liệu: {e}")
            return []

    def get_yard(self):
        query = "select id_bai, ten_bai, dia_chi from yards"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi truy vấn dữ liệu: {e}")
            return []
        
    def add_vehicle(self, bien_so):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO cars (bien_so) VALUES (?)",
            (bien_so,)
        )
        conn.commit()
        conn.close()

    def delete_vehicle(self, selected_id):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cars WHERE id_car=?", (selected_id,))
        conn.commit()
        conn.close()

    # Thêm hàm: add(), update(), delete()...
    def add_yard(self, ten_bai, dia_chi):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO yards (ten_bai, dia_chi) VALUES (?, ?)",
            (ten_bai, dia_chi)
        )
        conn.commit()
        conn.close()

    def update_vehicle(self, selected_id, bien_so):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE cars SET bien_so=? WHERE id_car=?",
            (bien_so, selected_id)
        )
        conn.commit()
        conn.close()
    
    def update_yard(self, selected_id, ten_bai, dia_chi):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE yards SET ten_bai=?, dia_chi=? WHERE id_bai=?",
            (ten_bai, dia_chi, selected_id)
        )
        conn.commit()
        conn.close()

    def delete_yard(self, selected_id):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM yards WHERE id_bai=?", (selected_id,))
        conn.commit()
        conn.close()