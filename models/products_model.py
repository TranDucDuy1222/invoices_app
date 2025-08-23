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
    def add_item(self, id_bai, ten, gia, donvi):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        if id_bai is not None:
            cursor.execute(
                "INSERT INTO products (ten_sp, don_vi_tinh, gia_ban, id_bai) VALUES (?, ?, ?, ?)",
                (ten, donvi, gia, id_bai)
            )
        else:
            cursor.execute(
                "INSERT INTO products (ten_sp, don_vi_tinh, gia_ban) VALUES (?, ?, ?)",
                (ten, donvi, gia)
            )
        conn.commit()
        conn.close()
    
    def update_item(self, selected_id, id_bai, ten, gia_int, donvi):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        if id_bai is not None:
            cursor.execute(
                "UPDATE products SET ten_sp=?, don_vi_tinh=?, gia_ban=?, id_bai=? WHERE id_sp=?",
                (ten, donvi, gia_int, id_bai, selected_id)
            )
        else:
            cursor.execute(
                "UPDATE products SET ten_sp=?, don_vi_tinh=?, gia_ban=? WHERE id_sp=?",
                (ten, donvi, gia_int, selected_id)
            )
        conn.commit()
        conn.close()

    def delete_item(self, selected_id):
        conn = sqlite3.connect("database/CSP_0708.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id_sp=?", (selected_id,))
        conn.commit()
        conn.close()