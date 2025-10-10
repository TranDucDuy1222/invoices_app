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
        try:
            self.cursor.execute("INSERT INTO cars (bien_so) VALUES (?)", (bien_so,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def delete_vehicle(self, selected_id):
        try:
            self.cursor.execute("DELETE FROM cars WHERE id_car=?", (selected_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    # Thêm hàm: add(), update(), delete()...
    def add_yard(self, ten_bai, dia_chi):
        try:
            self.cursor.execute("INSERT INTO yards (ten_bai, dia_chi) VALUES (?, ?)", (ten_bai, dia_chi))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def update_vehicle(self, selected_id, bien_so):
        try:
            self.cursor.execute("UPDATE cars SET bien_so=? WHERE id_car=?", (bien_so, selected_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e
    
    def update_yard(self, selected_id, ten_bai, dia_chi):
        try:
            self.cursor.execute("UPDATE yards SET ten_bai=?, dia_chi=? WHERE id_bai=?", (ten_bai, dia_chi, selected_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def delete_yard(self, selected_id):
        try:
            self.cursor.execute("DELETE FROM yards WHERE id_bai=?", (selected_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e