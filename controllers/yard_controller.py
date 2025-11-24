from models.yard_model import YardModel
import sqlite3
from views.config import db_path
from tkinter import messagebox

class YardController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = YardModel(db_path)
        self.app = view.root_window # Lưu lại tham chiếu đến cửa sổ chính (App)
        self.view.controller = self # Gán controller cho view
        self.refresh_data() # Tải dữ liệu ban đầu

    def load_yards(self):
        """Tải danh sách bãi từ model và cập nhật view."""
        try:
            all_data = self.model.get_yard()
            self.view.set_yard_list(all_data)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách bãi: {e}")

    def load_vehicles(self):
        """Tải danh sách xe từ model và cập nhật view."""
        try: 
            all_data = self.model.get_vehicle()
            self.view.load_vehicles_data(all_data)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách xe: {e}")

    def check_yard_deletable(self, yard_id):
        """Kiểm tra xem bãi có thể xóa được không."""
        return not self.model.is_yard_in_invoice_details(yard_id)

    def check_vehicle_deletable(self, vehicle_id):
        """Kiểm tra xem xe có thể xóa được không."""
        return not self.model.is_vehicle_in_invoice_details(vehicle_id)

    def add_vehicle(self, bien_so):
        try:
            # Kiểm tra xem biển số đã tồn tại chưa
            if self.model.check_vehicle_exists(bien_so):
                messagebox.showerror("Lỗi trùng lặp", f"Biển số xe '{bien_so}' đã tồn tại.")
                return False

            self.model.add_vehicle(bien_so)
            messagebox.showinfo("Thành công", f"Đã thêm xe '{bien_so}'!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm xe: {e}")
            return False

    def update_vehicle(self, selected_id, bien_so):
        if not bien_so:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return False
        try:
            # Kiểm tra xem biển số mới có bị trùng với xe khác không
            if self.model.check_vehicle_exists(bien_so, exclude_id_car=selected_id):
                messagebox.showerror("Lỗi trùng lặp", f"Biển số xe '{bien_so}' đã tồn tại.")
                return False

            # Gọi phương thức update_yard từ model
            self.model.update_vehicle(selected_id, bien_so)
            messagebox.showinfo("Thành công", f"Đã cập nhật thông tin xe: '{bien_so}'!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin xe: {e}")
            return False

    def delete_vehicle(self, selected_id):
        try:
            # Gọi phương thức delete_item từ model
            self.model.delete_vehicle(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa thông tin xe!")
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
            # Không cần refresh_data() ở đây, view sẽ tự xóa dòng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa thông tin xe: {e}")
    
    def add_yard(self, ten_bai, dia_chi):
        try:
            # Kiểm tra trùng lặp trước khi thêm
            reasons, existing_yard = self.model.check_yard_exists(ten_bai, dia_chi)
            if reasons:
                existing_id, existing_name, existing_address = existing_yard
                
                error_parts = []
                if 'ten_bai' in reasons:
                    error_parts.append("Tên bãi")
                if 'dia_chi' in reasons:
                    error_parts.append("Địa chỉ")

                if error_parts:
                    error_intro = f"{' và '.join(error_parts)} đã tồn tại."
                    messagebox.showerror("Lỗi trùng lặp", error_intro)
                else:
                    # Trường hợp dự phòng
                    messagebox.showerror("Lỗi trùng lặp", "Thông tin bãi đã tồn tại.")
                return False

            self.model.add_yard(ten_bai, dia_chi)
            messagebox.showinfo("Thành công", "Đã thêm bãi mới!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_product_page_data() # Làm mới dữ liệu ở tab Mặt hàng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm bãi: {e}")
            return False

    def update_yard(self, selected_id, ten_bai, dia_chi):
        if not ten_bai or not dia_chi:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return False
        try:
            # Kiểm tra trùng lặp trước khi cập nhật
            reasons, existing_yard = self.model.check_yard_exists(ten_bai, dia_chi, exclude_id_bai=selected_id)
            if reasons:
                existing_id, existing_name, existing_address = existing_yard

                error_parts = []
                if 'ten_bai' in reasons:
                    error_parts.append("Tên bãi")
                if 'dia_chi' in reasons:
                    error_parts.append("Địa chỉ")

                if error_parts:
                    error_intro = f"{' và '.join(error_parts)} đã tồn tại."
                    messagebox.showerror("Lỗi trùng lặp", error_intro)
                else:
                    # Trường hợp dự phòng
                    messagebox.showerror("Lỗi trùng lặp", "Thông tin bãi đã tồn tại.")
                return False

            # Gọi phương thức update_yard từ model
            self.model.update_yard(selected_id, ten_bai, dia_chi)
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin bãi!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_product_page_data() # Làm mới dữ liệu ở tab Mặt hàng
            return True
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin bãi: {e}")
            return False
    
    def delete_yard(self, selected_id):
        try:
            self.model.delete_yard(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa thông tin bãi!")
            self.app.refresh_product_page_data() # Làm mới dữ liệu ở tab Mặt hàng
            # Không cần refresh_data() ở đây, view sẽ tự xóa dòng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa thông tin bãi: {e}")
    
    def refresh_data(self):
        """Tải lại cả dữ liệu bãi và xe."""
        self.load_yards()
        self.load_vehicles()

    def __del__(self):
        self.model.close()