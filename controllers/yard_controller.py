from models.yard_model import YardModel
import sqlite3
from views.config import db_path
from tkinter import messagebox

class YardController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = YardModel(db_path)
        self.view.controller = self
        self.get_data()

    def reload_data(self):
        try:
            # Lấy lại dữ liệu bãi từ model
            all_data = self.model.get_yard()
            # Cập nhật lại view
            self.view.set_yard_list(all_data)
        except Exception as e:
            print("Lỗi khi load danh sách bãi:", e)

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
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật bãi: {e}")
    
    def delete_yard(self, selected_id):
        try:
            # Gọi phương thức delete_item từ model
            self.model.delete_yard(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa mặt hàng!")
            self.reload_data()  # Tải lại danh sách sau khi xóa
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa mặt hàng: {e}")
    
    def __del__(self):
        self.model.close()