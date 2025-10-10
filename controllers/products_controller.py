from models.products_model import ProductModel
from views.config import db_path
from tkinter import messagebox

class ProductController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = ProductModel(db_path)
        self.app = view.root_window # Lưu lại tham chiếu đến cửa sổ chính (App)
        self.view.controller = self # Gán controller cho view
        self.load_products()
        self.load_yards()

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
                # Nếu có, tạo chuỗi hiển thị mới
                formatted_name = f"{ten_sp} (Bãi: {ten_bai})"
            else:
                # Nếu không, chỉ dùng tên sản phẩm
                formatted_name = ten_sp

            # Xử lý và định dạng các cặp Đơn vị - Giá
            try:
                # Tách chuỗi đơn vị và giá thành các danh sách
                units = str(don_vi).split('|') if don_vi else []
                prices = str(gia_ban).split('|') if gia_ban else []
                
                # Ghép cặp đơn vị và giá, sau đó định dạng
                formatted_pairs = []
                for unit, price in zip(units, prices):
                    # Đảm bảo price là một chuỗi số hợp lệ trước khi chuyển đổi
                    formatted_price = f"{int(price.strip()):,}".replace(",", ".") if price.strip().isdigit() else "Lỗi"
                    formatted_pairs.append(f"{unit} : {formatted_price}")
                
                unit_price_display = " | ".join(formatted_pairs)
            except (ValueError, TypeError, IndexError):
                unit_price_display = "Lỗi định dạng"

            # Trả về ten_sp và ten_bai riêng biệt
            display_row = (id_sp, formatted_name, unit_price_display, ten_sp, ten_bai)
            display_data.append(display_row)

        # 3. Gọi phương thức của View để cập nhật Treeview với dữ liệu đã xử lý
        self.view.set_products_list(display_data)

    def load_yards(self):
        """Lấy danh sách bãi từ model và tạo một map để tra cứu ID."""
        self.yards_data = self.model.get_yard_info()
        # Tạo một dictionary để dễ dàng tìm id từ tên bãi được chọn
        self.yard_name_to_id_map = {yard[1]: yard[0] for yard in self.yards_data}
        self.view.set_yard_list(self.yards_data)

    def add_item(self, id_bai, ten, units, prices):
        try:
            # Chuyển đổi danh sách đơn vị và giá thành chuỗi để lưu vào DB
            units_str = "|".join(units)
            prices_str = "|".join(map(str, prices))
            
            self.model.add_item(id_bai, ten, prices_str, units_str)
            messagebox.showinfo("Thành công", f"Đã thêm mặt hàng '{ten}'!")
            # Sau khi thêm, load lại danh sách mặt hàng
            self.refresh_data() # Làm mới danh sách sản phẩm hiện tại
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
        except Exception as e:
            print(f"Lỗi khi thêm mặt hàng: {e}") # Ghi log lỗi ra terminal
            messagebox.showerror("Lỗi", f"Không thể thêm mặt hàng: {e}")

    def update_item(self, selected_id, id_bai, ten, units_str, prices_str):
        try:
            self.model.update_item(selected_id, id_bai, ten, prices_str,  units_str)
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin mặt hàng!")
            self.refresh_data()  # Tải lại danh sách sau khi cập nhật
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
        except Exception as e:
            print(f"Lỗi khi cập nhật mặt hàng: {e}") # Ghi log lỗi ra terminal
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin mặt hàng: {e}")
    def delete_item(self, selected_id):
        try:
            # Gọi phương thức delete_item từ model
            self.model.delete_item(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa mặt hàng!")
            self.refresh_data() # Tải lại danh sách sản phẩm sau khi xóa
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
        except Exception as e:
            print(f"Lỗi khi xóa mặt hàng: {e}") # Ghi log lỗi ra terminal
            messagebox.showerror("Lỗi", f"Không thể xóa mặt hàng: {e}")
    
    def refresh_data(self):
        """Tải lại cả sản phẩm và bãi."""
        self.load_products()
        self.load_yards()

    def __del__(self):
        self.model.close()