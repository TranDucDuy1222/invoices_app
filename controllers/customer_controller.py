from models.customer_model import CustomerModel
import sqlite3
from views.config import db_path
from tkinter import messagebox

class CustomerController:
    def __init__(self, view, db_path):
        self.view = view
        self.app = view.root_window # Lưu lại tham chiếu đến cửa sổ chính (App)
        self.model = CustomerModel(db_path)
        self.view.controller = self
        self.refresh_data() # Tải dữ liệu ban đầu

    def refresh_data(self):
        """Tải lại danh sách khách hàng và cập nhật view."""
        try:
            all_data = self.model.get_customer()
            self.view.set_customer_list(all_data)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải danh sách khách hàng: {e}")

    def check_customer_deletable(self, customer_id):
        """Kiểm tra xem khách hàng có thể xóa được không (không có trong hóa đơn)."""
        return not self.model.is_customer_in_invoices(customer_id)

    def add_customer(self, ten_kh, dia_chi, so_dien_thoai):
        try:
            # 1. Kiểm tra xem khách hàng đã tồn tại chưa, hàm trả về (danh sách lý do, dữ liệu)
            reasons, existing_customer_data = self.model.check_customer_exists(ten_kh, dia_chi, so_dien_thoai)
            
            if reasons:
                # 2. Nếu có, tạo thông báo chi tiết dựa trên lý do và hỏi người dùng
                id_kh, ten, dia_chi_cu, sdt_cu = existing_customer_data
                
                # Xây dựng phần giới thiệu lỗi dựa trên các lý do tìm thấy
                error_parts = []
                if 'sdt' in reasons:
                    error_parts.append(f"Số điện thoại '{so_dien_thoai}'")
                if 'ten_dia_chi' in reasons:
                    error_parts.append("cặp Tên & Địa chỉ")

                # Trường hợp đặc biệt: chỉ trùng tên
                if reasons == ['ten']:
                    messagebox.showwarning("Tên đã tồn tại", f"Tên khách hàng '{ten_kh}' đã tồn tại. Vui lòng chọn một tên khác để dễ phân biệt.")
                    return "keep_open", None

                if error_parts:
                    # Nối các phần lỗi lại với nhau: "Số điện thoại '...' và cặp Tên & Địa chỉ"
                    error_intro = f"{' và '.join(error_parts).capitalize()} đã được sử dụng bởi khách hàng:"
                else: # Trường hợp dự phòng
                    error_intro = "Thông tin khách hàng bị trùng với khách hàng:"

                msg = (f"{error_intro}\n\n"
                       f"- Tên: {ten}\n"
                       f"- Địa chỉ: {dia_chi_cu}\n"
                       f"- SĐT: {sdt_cu}\n\n"
                       "Bạn muốn làm gì?\n"
                       "- Yes: Sửa lại thông tin đang nhập.\n"
                       "- No: Xem chi tiết khách hàng đã tồn tại.\n"
                       "- Cancel: Hủy bỏ thao tác.")
                
                # Sử dụng askyesnocancel để có 3 lựa chọn
                choice = messagebox.askyesnocancel("Khách hàng đã tồn tại", msg)
                
                if choice is True: # Người dùng chọn "Yes" -> muốn sửa lại
                    return "keep_open", None
                elif choice is False: # Người dùng chọn "No" -> muốn xem chi tiết
                    return "show_existing", existing_customer_data
                else: # Người dùng chọn "Cancel" hoặc đóng hộp thoại
                    return "cancel", None

            # 3. Nếu không trùng, thêm khách hàng mới
            self.model.add_customer(ten_kh, dia_chi, so_dien_thoai)
            messagebox.showinfo("Thành công", "Đã thêm khách hàng mới!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
            return "success", None
        except sqlite3.IntegrityError as e:
            # Bắt lỗi ràng buộc duy nhất từ SQLite và hiển thị thông báo thân thiện hơn
            error_msg = str(e).lower()
            if 'unique constraint failed: customers.sdt' in error_msg:
                messagebox.showerror("Lỗi trùng lặp", f"Số điện thoại '{so_dien_thoai}' đã tồn tại. Vui lòng sử dụng số khác.")
            elif 'unique constraint failed: customers.ten' in error_msg:
                messagebox.showerror("Lỗi trùng lặp", f"Tên khách hàng '{ten_kh}' đã tồn tại. Vui lòng đổi tên khác để dễ phân biệt.")
            else:
                # Thông báo lỗi chung cho các trường hợp IntegrityError khác
                messagebox.showerror("Lỗi dữ liệu", f"Không thể cập nhật do vi phạm ràng buộc dữ liệu: {e}")
            return False
        except Exception as e:
            # Bắt các lỗi khác không lường trước được
            messagebox.showerror("Lỗi", f"Không thể thêm mới thông tin khách hàng: {e}")
            return False

    def update_customer(self, selected_id, ten_kh, dia_chi, so_dien_thoai):
        if not ten_kh or not dia_chi or not so_dien_thoai:
                messagebox.showwarning("Thiếu thông tin", "Không thể thực hiện thao tác!")
                return False
        try:
            # Kiểm tra xem thông tin mới có bị trùng với một khách hàng khác không
            reasons, existing_customer_data = self.model.check_customer_exists(
                ten_kh, dia_chi, so_dien_thoai, exclude_id_kh=selected_id
            )

            if reasons:
                # Nếu có trùng lặp, xây dựng thông báo chi tiết và dừng lại
                id_kh, ten, dia_chi_cu, sdt_cu = existing_customer_data

                # Xây dựng phần giới thiệu lỗi dựa trên các lý do tìm thấy
                error_parts = []
                if 'sdt' in reasons:
                    error_parts.append(f"Số điện thoại '{so_dien_thoai}'")
                if 'ten_dia_chi' in reasons:
                    error_parts.append("cặp Tên & Địa chỉ")

                # THAY ĐỔI: Xử lý trường hợp chỉ trùng tên một cách riêng biệt và nhất quán
                # Giống như khi thêm khách hàng mới.
                if reasons == ['ten']:
                    error_parts.append(f"tên '{ten_kh}'")

                if error_parts:
                    error_intro = f"{' và '.join(error_parts).capitalize()} đã được sử dụng bởi khách hàng:"
                else: # Trường hợp dự phòng
                    error_intro = "Thông tin khách hàng bị trùng với khách hàng:"

                msg = (f"{error_intro}\n\n"
                       f"- Tên: {ten}\n"
                       f"- Địa chỉ: {dia_chi_cu}\n"
                       f"- SĐT: {sdt_cu}")
                messagebox.showerror("Lỗi trùng lặp", msg)
                return False

            self.model.update_customer(selected_id, ten_kh, dia_chi, so_dien_thoai)
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin khách hàng!")
            self.refresh_data() # Tải lại dữ liệu cho tab hiện tại
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
            self.app.refresh_debt_data() # THÊM: Làm mới dữ liệu ở tab Công nợ
            self.app.refresh_invoice_history() # THÊM: Làm mới dữ liệu ở tab Lịch sử hóa đơn
            return True
        except sqlite3.IntegrityError as e:
            # Bắt lỗi ràng buộc duy nhất từ SQLite và hiển thị thông báo thân thiện hơn
            error_msg = str(e).lower()
            if 'unique constraint failed: customers.sdt' in error_msg:
                messagebox.showerror("Lỗi trùng lặp", f"Số điện thoại '{so_dien_thoai}' đã tồn tại. Vui lòng sử dụng số khác.")
            elif 'unique constraint failed: customers.ten' in error_msg:
                messagebox.showerror("Lỗi trùng lặp", f"Tên khách hàng '{ten_kh}' đã tồn tại. Vui lòng đổi tên khác để dễ phân biệt.")
            else:
                # Thông báo lỗi chung cho các trường hợp IntegrityError khác
                messagebox.showerror("Lỗi dữ liệu", f"Không thể cập nhật do vi phạm ràng buộc dữ liệu: {e}")
            return False
        except Exception as e:
            # Bắt các lỗi khác không lường trước được
            messagebox.showerror("Lỗi", f"Không thể cập nhật thông tin khách hàng: {e}")
            return False
    
    def delete_customer(self, selected_id):
        try:
            # Gọi phương thức delete_item từ model
            self.model.delete_customer(selected_id)
            messagebox.showinfo("Thành công", "Đã xóa thông tin khách hàng!")
            self.app.refresh_invoice_creation_data() # Làm mới dữ liệu ở tab Tạo hóa đơn
            # Không cần refresh_data() ở đây, view sẽ tự xóa dòng
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa thông tin khách hàng: {e}")
    
    def __del__(self):
        self.model.close()