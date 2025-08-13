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

    # Thêm hàm: add(), update(), delete()...