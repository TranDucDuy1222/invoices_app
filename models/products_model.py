from .base_model import BaseModel

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
            # In ra để gỡ lỗi (bạn có thể xóa sau)
            print("--- MODEL ĐANG THỰC THI QUERY:", yard_info)
            
            self.cursor.execute(yard_info)
            results = self.cursor.fetchall()
            
            # In kết quả để gỡ lỗi (bạn có thể xóa sau)
            print("--- MODEL ĐÃ LẤY ĐƯỢC DANH SÁCH BÃI:", results)
            
            return results
        except Exception as e:
            print(f"Lỗi khi truy vấn danh sách bãi: {e}")
            return []

    # Thêm hàm: add(), update(), delete()...
    def add_item(self, id_bai, ten_sp, gia_ban, don_vi_tinh):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (id_bai, ten_sp, gia_ban, don_vi_tinh) VALUES (?, ?, ?)",
                       (id_bai, ten_sp, gia_ban, don_vi_tinh))
        conn.commit()
        conn.close()