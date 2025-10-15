from models.customer_model import CustomerModel
import sqlite3
from views.config import db_path
from tkinter import messagebox

class CustomerController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = CustomerModel(db_path)
        self.view.controller = self
        self.get_data()

    def get_data(self):
        """
        Lấy dữ liệu từ Model, xử lý chuỗi hiển thị, và cập nhật View.
        """
        # 1. Lấy dữ liệu thô từ model
        all_data = self.model.get_customer()
        
        self.view.set_customer_list(all_data)

    def reload_data(self):
        try:
            # Lấy lại dữ liệu bãi từ model
            all_data = self.model.get_customer()
            # Cập nhật lại view
            self.view.set_customer_list(all_data)
        except Exception as e:
            print("Lỗi khi load danh sách bãi:", e)

    def add_customer(self, ten_kh, dia_chi, so_dien_thoai):
        # if not ten_kh or not dia_chi or not so_dien_thoai:
        #         messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
        #         return
        try:
            self.model.add_customer(ten_kh, dia_chi, so_dien_thoai)
            messagebox.showinfo("Thành công", "Đã thêm khách hàng mới!")
            # Sau khi thêm, load lại danh sách mặt hàng
            self.reload_data()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể thêm khách hàng: {e}")

    def update_customer(self, selected_id, ten_kh, dia_chi, so_dien_thoai):
        if not ten_kh or not dia_chi or not so_dien_thoai:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return
        try:
            # Gọi phương thức update_yard từ model
            self.model.update_customer(selected_id, ten_kh, dia_chi, so_dien_thoai)
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin khách hàng!")
            self.reload_data()  # Tải lại danh sách sau khi cập nhật
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin khách hàng: {e}")
    
    def delete_customer(self, selected_id):
        try:
            # Gọi phương thức delete_item từ model
            self.model.delete_customer(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa thông tin khách hàng!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa thông tin khách hàng: {e}")
    
    def __del__(self):
        self.model.close()