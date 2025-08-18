from models.products_model import ProductModel
import sqlite3
from views.config import db_path

class ProductController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = ProductModel(db_path)
        self.load_products()
        self.load_yards()

    def reload_products_list(self, db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id_sp, id_bai, ten_mat_hang, don_vi_tinh, gia_ban FROM products")
            data = cursor.fetchall()
            conn.close()
            self.view.set_products_list(data)
        except Exception as e:
            print("Lỗi khi load danh sách mặt hàng:", e)

    def load_products(self):
        """
        Lấy dữ liệu từ Model, xử lý chuỗi hiển thị, và cập nhật View.
        """
        # 1. Lấy dữ liệu thô từ model
        all_data = self.model.get_all_products_with_yard_info()

        # 2. Tạo một danh sách mới để chứa dữ liệu đã được định dạng
        display_data = []
        for row in all_data:
            id_sp, ten_sp, don_vi, gia_ban, ten_bai = row

            # Kiểm tra xem sản phẩm có tên bãi không
            if ten_bai:
                # Nếu có, tạo chuỗi đa dòng
                formatted_name = f"{ten_sp}\n(Bãi: {ten_bai})"
            else:
                # Nếu không, chỉ dùng tên sản phẩm
                formatted_name = ten_sp
            
            # Định dạng giá bán với dấu phẩy
            formatted_price = f"{gia_ban:,}".replace(",", ".")
            # Tạo tuple mới với tên đã được định dạng
            display_row = (id_sp, formatted_name, don_vi, formatted_price, ten_bai)
            display_data.append(display_row)

        # 3. Gọi phương thức của View để cập nhật Treeview với dữ liệu đã xử lý
        self.view.set_products_list(display_data)

    def load_yards(self):
        """Lấy danh sách bãi từ model và tạo một map để tra cứu ID."""
        self.yards_data = self.model.get_yard_info()
        # Tạo một dictionary để dễ dàng tìm id từ tên bãi được chọn
        self.yard_name_to_id_map = {yard[1]: yard[0] for yard in self.yards_data}
        self.view.set_yard_list(self.yards_data)

    def add_item(self, id_bai, ten_sp, gia_ban, don_vi_tinh):
        # Kiểm tra dữ liệu hợp lệ
        if not ten_sp.strip():
            return False, "Tên mặt hàng không được để trống!"
        try:
            price = float(gia_ban)
        except ValueError:
            return False, "Giá phải là số!"
        
        # Lưu vào DB
        self.model.add_item(id_bai.strip(), ten_sp.strip(), gia_ban, don_vi_tinh)
        return True, "Thêm mặt hàng thành công!"
    
    def __del__(self):
        self.model.close()