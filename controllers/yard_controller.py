from models.yard_model import YardModel
import sqlite3
from views.config import db_path
from tkinter import messagebox

class YardController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = YardModel(db_path)
        self.app = view.root_window # Lưu lại tham chiếu đến cửa sổ chính (App)
        self.view.controller = self
        self.get_data()
        self.get_vehicle_data()

    def reload_data(self):
        try:
            # Lấy lại dữ liệu bãi từ model
            all_data = self.model.get_yard()
            # Cập nhật lại view
            self.view.set_yard_list(all_data)
        except Exception as e:
            print("Lỗi khi load danh sách bãi:", e)

    def reload_vehicle_data(self):
        try: 
            all_data = self.model.get_vehicle()
            self.view.load_vehicles_data(all_data)
        except Exception as e:
            print("Lỗi khi load danh sách xe:", e)

    def get_vehicle_data(self):
        all_data = self.model.get_vehicle()
        self.view.load_vehicles_data(all_data)

    def add_vehicle(self, bien_so):
        if not bien_so:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return
        try:
            self.model.add_vehicle(bien_so)
            messagebox.showinfo("Thành công", "Đã thêm xe mới!")
            # Sau khi thêm, load lại danh sách mặt hàng
            self.reload_vehicle_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm xe: {e}")

    def update_vehicle(self, selected_id, bien_so):
        if not bien_so:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return
        try:
            # Gọi phương thức update_yard từ model
            self.model.update_vehicle(selected_id, bien_so)
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin xe!")
            self.reload_vehicle_data()  # Tải lại danh sách sau khi cập nhật
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật bãi: {e}")

    def delete_vehicle(self, selected_id):
        try:
            # Gọi phương thức delete_item từ model
            self.model.delete_vehicle(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa thông tin xe!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa thông tin xe: {e}")

    def get_data(self):
        """
        Lấy dữ liệu từ Model, xử lý chuỗi hiển thị, và cập nhật View.
        """
        # 1. Lấy dữ liệu thô từ model
        all_data = self.model.get_yard()
        
        self.view.set_yard_list(all_data)

    def add_yard(self, ten_bai, dia_chi):
        if not ten_bai or not dia_chi:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return
        try:
            self.model.add_yard(ten_bai, dia_chi)
            messagebox.showinfo("Thành công", "Đã thêm bãi mới!")
            # Sau khi thêm, load lại danh sách mặt hàng
            self.reload_data()
            self.app.refresh_product_page_data() # <-- THÊM DÒNG NÀY
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm bãi: {e}")

    def update_yard(self, selected_id, ten_bai, dia_chi):
        if not ten_bai or not dia_chi:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return
        try:
            # Gọi phương thức update_yard từ model
            self.model.update_yard(selected_id, ten_bai, dia_chi)
            messagebox.showinfo("Thành công", "Đã cập nhật bãi!")
            self.reload_data()  # Tải lại danh sách sau khi cập nhật
            self.app.refresh_product_page_data() # <-- THÊM DÒNG NÀY
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật bãi: {e}")
    
    def delete_yard(self, selected_id):
        try:
            # Gọi phương thức delete_item từ model
            self.model.delete_yard(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa mặt hàng!")
            self.app.refresh_product_page_data() # <-- THÊM DÒNG NÀY
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa mặt hàng: {e}")
    
    def __del__(self):
        self.model.close()