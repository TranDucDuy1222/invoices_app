from .base_model import BaseModel
import sqlite3


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
            print(f"Lỗi khi truy vấn sản phẩm: {e}")
            return []
        
    def get_yard_info(self):
        yard_info = """select * from yards """
        try:
            self.cursor.execute(yard_info)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            print(f"Lỗi khi truy vấn danh sách bãi: {e}")
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
        try:
            if id_bai is not None:
                self.cursor.execute(
                    "UPDATE products SET ten_sp=?, don_vi_tinh=?, gia_ban=?, id_bai=? WHERE id_sp=?",
                    (ten, donvi, gia_int, id_bai, selected_id)
                )
            else:
                self.cursor.execute(
                    "UPDATE products SET ten_sp=?, don_vi_tinh=?, gia_ban=? WHERE id_sp=?",
                    (ten, donvi, gia_int, selected_id)
                )
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