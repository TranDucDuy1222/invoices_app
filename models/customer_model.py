from .base_model import BaseModel
from tkinter import messagebox
import sqlite3


class CustomerModel(BaseModel):
    def __init__(self, db_path):
        # Gọi __init__ của lớp cha (BaseModel) để có self.conn và self.cursor
        super().__init__(db_path)

    def get_customer(self):
        query = """
                SELECT c.id_kh, c.ten, a.dia_chi, c.sdt
                FROM customers c
                JOIN addresses a ON c.id_kh = a.id_kh
            """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi truy vấn dữ liệu: {e}")
            return []

    # Thêm hàm: add(), update(), delete()...
    def add_customer(self, ten_kh, dia_chi, so_dien_thoai):
        try:
            # Thêm khách hàng mới
            self.cursor.execute("INSERT INTO customers (ten, sdt) VALUES (?, ?)", (ten_kh, so_dien_thoai))
            id_kh = self.cursor.lastrowid  # Lấy id khách hàng vừa thêm

            # Thêm địa chỉ, liên kết với id_kh
            self.cursor.execute(
                "INSERT INTO addresses (dia_chi, id_kh) VALUES (?, ?)",
                (dia_chi, id_kh)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Lỗi khi thêm khách hàng: {e}")
            raise e
            
    def update_customer(self, selected_id, ten_kh, dia_chi, so_dien_thoai):
        try:
            # Cập nhật thông tin khách hàng
            self.cursor.execute(
                "UPDATE customers SET ten=?, sdt=? WHERE id_kh=?",
                (ten_kh, so_dien_thoai, selected_id)
            )
            # Cập nhật địa chỉ liên kết với khách hàng
            self.cursor.execute(
                "UPDATE addresses SET dia_chi=? WHERE id_kh=?",
                (dia_chi, selected_id)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Lỗi khi cập nhật thông tin khách hàng: {e}")
            raise e

    def delete_customer(self, selected_id):
        try:
            # Xóa địa chỉ liên kết với khách hàng
            self.cursor.execute("DELETE FROM addresses WHERE id_kh=?", (selected_id,))
            # Xóa khách hàng
            self.cursor.execute("DELETE FROM customers WHERE id_kh=?", (selected_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Lỗi khi xóa khách hàng: {e}")
            raise e