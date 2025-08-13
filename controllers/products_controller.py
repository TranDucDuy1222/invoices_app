from models.products_model import ProductModel

class ProductController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = ProductModel(db_path)
        self.load_products()

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
            display_row = (id_sp, formatted_name, don_vi, formatted_price)
            display_data.append(display_row)

        # 3. Gọi phương thức của View để cập nhật Treeview với dữ liệu đã xử lý
        self.view.set_products_list(display_data)

    def __del__(self):
        self.model.close()