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
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi truy vấn xe: {e}")
            return []

    def get_yard(self):
        query = "select id_bai, ten_bai, dia_chi from yards"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi truy vấn bãi: {e}")
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

    def is_yard_in_invoice_details(self, yard_id):
        """Kiểm tra xem id_bai có tồn tại trong bảng invoice_details không."""
        try:
            self.cursor.execute("SELECT 1 FROM invoice_details WHERE id_bai = ? LIMIT 1", (yard_id,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kiểm tra bãi: {e}")
            return True

    def is_vehicle_in_invoice_details(self, vehicle_id):
        """Kiểm tra xem id_xe có tồn tại trong bảng invoice_details không."""
        try:
            self.cursor.execute("SELECT 1 FROM invoice_details WHERE id_xe = ? LIMIT 1", (vehicle_id,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kiểm tra xe: {e}")
            return True

    def check_vehicle_exists(self, bien_so, exclude_id_car=None):
        """
        Kiểm tra xem biển số xe đã tồn tại hay chưa.
        So sánh không phân biệt chữ hoa/thường và bỏ qua khoảng trắng, dấu gạch.
        """
        try:
            # Chuẩn hóa biển số để so sánh: bỏ khoảng trắng, gạch ngang và chuyển thành chữ thường
            normalized_bien_so = bien_so.replace(' ', '').replace('-', '').lower()
            
            query = "SELECT id_car FROM cars WHERE REPLACE(REPLACE(LOWER(bien_so), ' ', ''), '-', '') = ?"
            params = [normalized_bien_so]
            
            if exclude_id_car is not None:
                query += " AND id_car != ?"
                params.append(exclude_id_car)
                
            self.cursor.execute(query, params)
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kiểm tra biển số xe: {e}")
            return True # Giả định là có lỗi để ngăn chặn việc thêm/sửa
        
    def check_yard_exists(self, ten_bai, dia_chi, exclude_id_bai=None):
        """
        Kiểm tra xem tên bãi hoặc địa chỉ đã tồn tại hay chưa.
        Trả về một tuple (lý_do, dữ_liệu_bãi) nếu tồn tại.
        - lý_do: 'ten_bai' hoặc 'dia_chi'.
        """
        try:
            reasons = []
            existing_yard_data = None
            base_query = "SELECT id_bai, ten_bai, dia_chi FROM yards"
            
            # 1. Kiểm tra tên bãi
            query_ten = f"{base_query} WHERE LOWER(ten_bai) = ?"
            params_ten = [ten_bai.lower()]
            if exclude_id_bai is not None:
                query_ten += " AND id_bai != ?"
                params_ten.append(exclude_id_bai)
            self.cursor.execute(query_ten, params_ten)
            existing = self.cursor.fetchone()
            if existing:
                reasons.append('ten_bai')
                if not existing_yard_data:
                    existing_yard_data = existing

            # 2. Kiểm tra địa chỉ
            query_diachi = f"{base_query} WHERE LOWER(dia_chi) = ?"
            params_diachi = [dia_chi.lower()]
            if exclude_id_bai is not None:
                query_diachi += " AND id_bai != ?"
                params_diachi.append(exclude_id_bai)
            self.cursor.execute(query_diachi, params_diachi)
            existing = self.cursor.fetchone()
            if existing:
                reasons.append('dia_chi')
                if not existing_yard_data:
                    existing_yard_data = existing

            return reasons, existing_yard_data

        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kiểm tra bãi: {e}")
            return ['error'], (None, 'Lỗi', str(e))