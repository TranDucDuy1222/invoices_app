
from .base_model import BaseModel
import sqlite3
from datetime import datetime
from tkinter import messagebox

class InvoiceModel(BaseModel):
    def __init__(self, db_path):
        # Gọi __init__ của lớp cha (BaseModel) để có self.conn và self.cursor
        super().__init__(db_path)

    def get_all_products_and_yard(self):
        """
        Truy vấn để lấy danh sách tất cả sản phẩm.
        Sử dụng JOIN để lấy tên bãi từ bảng 'yards'.
        """
        query = """
            SELECT
                p.id_sp,
                p.ten_sp,
                p.don_vi_tinh,
                p.gia_ban,
                y.ten_bai,
                p.id_bai
            FROM
                products p
            LEFT JOIN
                yards y ON p.id_bai = y.id_bai
        """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi truy vấn sản phẩm: {e}")
            return []

    def get_all_cars(self):
        """Truy vấn để lấy danh sách tất cả xe."""
        query = "SELECT id_car, bien_so FROM cars"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi truy vấn danh sách xe: {e}")
            return []

    def get_all_customers_invoice(self):
        query = """
                SELECT c.id_kh, c.ten, a.dia_chi, c.sdt
                FROM customers c
                JOIN addresses a ON c.id_kh = a.id_kh
            """
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi truy vấn danh sách khách hàng: {e}")
            return []

    def create_invoice(self, id_kh, ngay_tao_hd, ngay_mua, tong_tien, trang_thai, items):
        """
        Lưu hóa đơn và chi tiết hóa đơn vào cơ sở dữ liệu trong một transaction.
        """
        try:
            # 1. Thêm vào bảng invoices
            ngay_tao_hd_str = ngay_tao_hd.strftime('%d/%m/%Y %H:%M')
            ngay_mua_str = datetime.now().replace(
                    year=ngay_mua.year,
                    month=ngay_mua.month,
                    day=ngay_mua.day
                ).strftime('%d/%m/%Y %H:%M')
            
            invoice_query = """
                INSERT INTO invoices (id_kh, ngay_tao_hd, ngay_mua, tong_tien, trang_thai)
                VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(invoice_query, (id_kh, ngay_tao_hd_str, ngay_mua_str, tong_tien, trang_thai))
            
            # Lấy ID của hóa đơn vừa tạo
            id_hd = self.cursor.lastrowid

            # 2. Thêm vào bảng invoices_details
            details_query = """
                INSERT INTO invoice_details (id_hd, id_sp, id_xe, id_bai, don_vi_tinh, don_gia, so_luong, phi_van_chuyen, noi_giao, thanh_tien)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            details_data = []
            for item in items:
                details_data.append((
                    id_hd,
                    item['id'],
                    item.get('id_xe'),
                    item.get('id_bai'),
                    item['don_vi'],
                    item['don_gia'],
                    item['so_luong'],
                    item['phi_vc'],
                    item['noi_giao'],
                    item['thanh_tien']
                ))
            
            self.cursor.executemany(details_query, details_data)
            
            self.conn.commit()
            return id_hd
        except sqlite3.Error as e:
            self.conn.rollback() # Hoàn tác nếu có lỗi
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi tạo hóa đơn: {e}")
            raise

    def get_debt_by_customer_id(self, id_kh):
        """Lấy bản ghi công nợ của một khách hàng."""
        query = "SELECT * FROM debts WHERE id_kh = ? ORDER BY ngay_cap_nhat DESC LIMIT 1"
        try:
            self.cursor.execute(query, (id_kh,))
            return self.cursor.fetchone()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi truy vấn công nợ: {e}")
            return None

    def update_customer_debt(self, id_cn, cong_no_cu, cong_no_dtt, tong_cong_no_moi, ngay_cap_nhat):
        """Cập nhật một bản ghi công nợ đã có."""
        query = """
            UPDATE debts 
            SET cong_no_cu = ?, cong_no_dtt = ?, tong_cong_no = ?, ngay_cap_nhat = ?
            WHERE id_cn = ?
        """
        try:
            self.cursor.execute(query, (cong_no_cu, cong_no_dtt, tong_cong_no_moi, ngay_cap_nhat, id_cn))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi cập nhật công nợ: {e}")
            raise e

    def create_customer_debt(self, id_kh, cong_no_cu, cong_no_dtt, tong_cong_no, ngay_cap_nhat):
        """Tạo một bản ghi công nợ mới cho khách hàng."""
        query = "INSERT INTO debts (id_kh, cong_no_cu, cong_no_dtt, tong_cong_no, ngay_cap_nhat) VALUES (?, ?, ?, ?, ?)"
        try:
            self.cursor.execute(query, (id_kh, cong_no_cu, cong_no_dtt, tong_cong_no, ngay_cap_nhat))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi tạo công nợ mới: {e}")
            raise e