from .base_model import BaseModel
import sqlite3
from tkinter import messagebox

class ProductModel(BaseModel):
    def __init__(self, db_path):
        # Gọi __init__ của lớp cha (BaseModel) để có self.conn và self.cursor
        super().__init__(db_path)

    def get_all_products_with_yard_info(self):
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
                y.ten_bai
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
        
    def get_yard_info(self):
        yard_info = """select * from yards """
        try:
            self.cursor.execute(yard_info)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi truy vấn bãi: {e}")
            return []

    # Thêm hàm: add(), update(), delete()...
    def add_item(self, id_bai, ten, prices_str, units_str):
        try:
            if id_bai is not None:
                self.cursor.execute(
                    "INSERT INTO products (ten_sp, don_vi_tinh, gia_ban, id_bai) VALUES (?, ?, ?, ?)",
                    (ten, units_str, prices_str, id_bai)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO products (ten_sp, don_vi_tinh, gia_ban) VALUES (?, ?, ?)",
                    (ten, units_str, prices_str)
                )
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e
    
    def update_item(self, selected_id, id_bai, ten, gia_int, donvi):
        try: # Sửa lại hàm update_item
            if id_bai is not None: # Trường hợp có chọn bãi
                query = "UPDATE products SET ten_sp=?, don_vi_tinh=?, gia_ban=?, id_bai=? WHERE id_sp=?"
                params = (ten, donvi, gia_int, id_bai, selected_id)
            else: # Trường hợp chọn "Không có bãi"
                query = "UPDATE products SET ten_sp=?, don_vi_tinh=?, gia_ban=?, id_bai=NULL WHERE id_sp=?"
                params = (ten, donvi, gia_int, selected_id)
            self.cursor.execute(query, params)
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def delete_item(self, selected_id):
        try:
            self.cursor.execute("DELETE FROM products WHERE id_sp=?", (selected_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise e

    def is_item_in_invoice_details(self, item_id):
        """Kiểm tra xem id_sp có tồn tại trong bảng invoice_details không."""
        try:
            self.cursor.execute("SELECT 1 FROM invoice_details WHERE id_sp = ? LIMIT 1", (item_id,))
            return self.cursor.fetchone() is not None
        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kiểm tra mặt hàng: {e}")
            return True

    def check_product_exists(self, ten_sp, id_bai, exclude_id_sp=None):
        """
        Kiểm tra xem một sản phẩm có tồn tại với cùng tên và bãi hay không. Trả về thông tin sản phẩm nếu có.
        """
        try:
            query = """
                SELECT p.id_sp, p.ten_sp, y.ten_bai
                FROM products p
                LEFT JOIN yards y ON p.id_bai = y.id_bai
                WHERE LOWER(p.ten_sp) = ?
            """

            if id_bai is None:
                query += " AND p.id_bai IS NULL"
                params = [ten_sp.lower()]
            else:
                query += " AND p.id_bai = ?"
                params = [ten_sp.lower(), id_bai]

            if exclude_id_sp is not None:
                query += " AND p.id_sp != ?"
                params.append(exclude_id_sp)
            
            query += " LIMIT 1"
            self.cursor.execute(query, params)
            return self.cursor.fetchone() # Trả về tuple (id, ten, ten_bai) hoặc None

        except sqlite3.Error as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi kiểm tra sản phẩm: {e}")
            return True # Giả sử là có lỗi để ngăn chặn việc thêm/sửa