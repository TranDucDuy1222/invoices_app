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
            messagebox.showerror("Lỗi", f"Không thể tải danh sách khách hàng: {e}")
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

    def is_customer_in_invoices(self, customer_id):
        """Kiểm tra xem id_kh có tồn tại trong bảng invoices không."""
        try:
            self.cursor.execute("SELECT 1 FROM invoices WHERE id_kh = ? LIMIT 1", (customer_id,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            print(f"Lỗi khi kiểm tra khách hàng trong hóa đơn: {e}")
            # Mặc định là không cho xóa nếu có lỗi để đảm bảo an toàn
            return True

    def check_customer_exists(self, ten_kh, dia_chi, sdt, exclude_id_kh=None):
        """
        Kiểm tra xem khách hàng có tồn tại với cùng SĐT và/hoặc cặp Tên & Địa chỉ hay không.
        Trả về một tuple (danh_sách_lý_do, dữ_liệu_khách_hàng) nếu tồn tại.
        - danh_sách_lý_do: list chứa 'sdt', 'ten_dia_chi'.
        """
        try:
            reasons = []
            existing_customer_data = None
            base_query = "SELECT c.id_kh, c.ten, a.dia_chi, c.sdt FROM customers c JOIN addresses a ON c.id_kh = a.id_kh"
            
            # 1. Kiểm tra số điện thoại (nếu có)
            if sdt:
                query_sdt = f"{base_query} WHERE c.sdt = ?"
                params_sdt = [sdt]
                if exclude_id_kh is not None:
                    query_sdt += " AND c.id_kh != ?"
                    params_sdt.append(exclude_id_kh)
                self.cursor.execute(query_sdt, params_sdt)
                existing = self.cursor.fetchone()
                if existing:
                    reasons.append('sdt')
                    if not existing_customer_data:
                        existing_customer_data = existing

            # 2. Kiểm tra cặp Tên & Địa chỉ
            query_ten_diachi = f"{base_query} WHERE LOWER(c.ten) = ? AND LOWER(a.dia_chi) = ?"
            params_ten_diachi = [ten_kh.lower(), dia_chi.lower()]
            if exclude_id_kh is not None:
                query_ten_diachi += " AND c.id_kh != ?"
                params_ten_diachi.append(exclude_id_kh)
            self.cursor.execute(query_ten_diachi, params_ten_diachi)
            existing = self.cursor.fetchone()
            if existing:
                reasons.append('ten_dia_chi')
                if not existing_customer_data:
                    existing_customer_data = existing

            # 3. Nếu chưa tìm thấy trùng lặp, kiểm tra chỉ riêng tên
            if not reasons:
                query_ten = f"{base_query} WHERE LOWER(c.ten) = ?"
                params_ten = [ten_kh.lower()]
                if exclude_id_kh is not None:
                    query_ten += " AND c.id_kh != ?"
                    params_ten.append(exclude_id_kh)
                self.cursor.execute(query_ten, params_ten)
                existing = self.cursor.fetchone()
                if existing:
                    reasons.append('ten')
                    if not existing_customer_data:
                        existing_customer_data = existing

            return reasons, existing_customer_data

        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kiểm tra khách hàng: {e}")
            # Giả định là có lỗi để ngăn chặn việc thêm/sửa, trả về một lý do chung
            return ['error'], (None, 'Lỗi', str(e), '')