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
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        try:
            # Thêm khách hàng mới
            cursor.execute("INSERT INTO customers (ten, sdt) VALUES (?, ?)", (ten_kh, so_dien_thoai))
            id_kh = cursor.lastrowid  # Lấy id khách hàng vừa thêm

            # Thêm địa chỉ, liên kết với id_kh
            cursor.execute(
                "INSERT INTO addresses (dia_chi, id_kh) VALUES (?, ?)",
                (dia_chi, id_kh)
            )
            conn.commit()
        except Exception as e:
            print(f"Lỗi khi thêm khách hàng: {e}")
        finally:
            conn.close()
            
    def update_customer(self, selected_id, ten_kh, dia_chi, so_dien_thoai):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        try:
            # Cập nhật thông tin khách hàng
            cursor.execute(
                "UPDATE customers SET ten=?, sdt=? WHERE id_kh=?",
                (ten_kh, so_dien_thoai, selected_id)
            )
            # Cập nhật địa chỉ liên kết với khách hàng
            cursor.execute(
                "UPDATE addresses SET dia_chi=? WHERE id_kh=?",
                (dia_chi, selected_id)
            )
            conn.commit()
        except Exception as e:
            print(f"Lỗi khi cập nhật thông tin khách hàng: {e}")
        finally:
            conn.close()

    def delete_customer(self, selected_id):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        try:
            # Xóa địa chỉ liên kết với khách hàng
            cursor.execute("DELETE FROM addresses WHERE id_kh=?", (selected_id,))
            # Xóa khách hàng
            cursor.execute("DELETE FROM customers WHERE id_kh=?", (selected_id,))
            conn.commit()
        except Exception as e:
            print(f"Lỗi khi xóa khách hàng: {e}")
        finally:
            conn.close()