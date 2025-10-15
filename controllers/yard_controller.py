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
            print("Lỗi khi load danh sách bãi:", e)

    def load_vehicles(self):
        """Tải danh sách xe từ model và cập nhật view."""
        try: 
            all_data = self.model.get_vehicle()
            self.view.load_vehicles_data(all_data)
        except Exception as e:
            print("Lỗi khi load danh sách xe:", e)

    def add_vehicle(self, bien_so):
        # if not bien_so:
        #         messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
        #         return
        try:
            self.model.add_vehicle(bien_so)
            messagebox.showinfo("Thành công", f"Đã thêm xe '{bien_so}'!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm xe: {e}")

    def update_vehicle(self, selected_id, bien_so):
        if not bien_so:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return
        try:
            # Gọi phương thức update_yard từ model
            self.model.update_vehicle(selected_id, bien_so)
            messagebox.showinfo("Thành công", f"Đã cập nhật thông tin xe: '{bien_so}'!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin xe: {e}")

    def delete_vehicle(self, selected_id):
        try:
            # Gọi phương thức delete_item từ model
            self.model.delete_vehicle(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa thông tin xe!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa thông tin xe: {e}")
    
    def add_yard(self, ten_bai, dia_chi):
        # if not ten_bai or not dia_chi:
        #         messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
        #         return
        try:
            self.model.add_yard(ten_bai, dia_chi)
            messagebox.showinfo("Thành công", "Đã thêm bãi mới!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_product_page_data() # Làm mới dữ liệu ở tab Mặt hàng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm bãi: {e}")

    def update_yard(self, selected_id, ten_bai, dia_chi):
        if not ten_bai or not dia_chi:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return
        try:
            # Gọi phương thức update_yard từ model
            self.model.update_yard(selected_id, ten_bai, dia_chi)
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin bãi!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_product_page_data() # Làm mới dữ liệu ở tab Mặt hàng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin bãi: {e}")
    
    def delete_yard(self, selected_id):
        try:
            self.model.delete_yard(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa thông tin bãi!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_product_page_data() # Làm mới dữ liệu ở tab Mặt hàng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa thông tin bãi: {e}")
    
    def refresh_data(self):
        """Tải lại cả dữ liệu bãi và xe."""
        self.load_yards()
        self.load_vehicles()

    def __del__(self):
        self.model.close()