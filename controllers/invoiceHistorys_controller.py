import tkinter as tk
from models.invoiceHistorys_model import InvoiceHistoryModel
from datetime import datetime
from tkinter import messagebox
from utils.printer import InvoicePrinter

class InvoiceHistoryController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = InvoiceHistoryModel(db_path)
        self.view.controller = self # Gán controller cho view

    def load_invoices(self, invoice_type):
        """Tải dữ liệu hóa đơn dựa vào loại được yêu cầu từ view."""
        if invoice_type == 'unpaid':
            # 0 = Chưa thanh toán
            invoices = self.model.get_invoices_by_status(0)
        elif invoice_type == 'paid':
            # 1 = Đã thanh toán
            invoices = self.model.get_invoices_by_status(1)
        elif invoice_type == 'summary':
            start_date, end_date = self.view.get_date_range()
            invoices = self.model.get_summary_invoices_by_date_range(start_date, end_date)
        else:
            invoices = []
        self.view.display_invoices(invoices, invoice_type)

    def get_invoice_details(self, invoice_id):
        """Lấy chi tiết hóa đơn và trả về cho view."""
        return self.model.get_invoice_details(invoice_id)

    def get_customer_debt(self, customer_id):
        """Lấy công nợ hiện tại của khách hàng."""
        return self.model.get_customer_current_debt(customer_id)

    def get_summary_details(self, customer_id, start_date, end_date):
        """Lấy chi tiết các mặt hàng cho hóa đơn gộp."""
        return self.model.get_unpaid_items_by_customer_and_date(customer_id, start_date, end_date)

    def print_invoice(self, invoice_data, items):
        """
        Chuẩn bị dữ liệu và gọi module in.
        """
        printer = InvoicePrinter() # Bạn có thể truyền tên máy in ở đây nếu muốn
        success, message = printer.print_invoice(invoice_data, items)

        if success:
            messagebox.showinfo("In hóa đơn", message)
        else:
            messagebox.showerror("Lỗi in", message)

    def export_invoice_to_pdf(self, invoice_data, items):
        """
        Chuẩn bị dữ liệu và gọi module để chỉ xuất file PDF.
        """
        printer = InvoicePrinter()
        success, message = printer.export_invoice_pdf(invoice_data, items)

        if success:
            messagebox.showinfo("Xuất PDF thành công", message)
        else:
            messagebox.showerror("Lỗi xuất PDF", message)

    def pay_invoice(self, invoice_id, customer_id, total_amount):
        """Xử lý logic thanh toán cho một hóa đơn."""
        try:
            # --- CẢI TIẾN: Kiểm tra công nợ trước khi thanh toán ---
            # 1. Lấy debt_controller và công nợ hiện tại
            debt_controller = self.view.root_window.debt_controller
            current_debt, _ = self.model.get_customer_current_debt(customer_id)
            
            payment_to_process = total_amount # Số tiền sẽ xử lý, mặc định là tổng hóa đơn

            # 2. So sánh và xác nhận nếu hóa đơn lớn hơn công nợ
            if total_amount > current_debt:
                msg = (f"Tổng hóa đơn ({total_amount:,.0f} VNĐ) lớn hơn công nợ hiện tại ({current_debt:,.0f} VNĐ).\n\n"
                       f"Bạn có muốn thanh toán toàn bộ công nợ còn lại ({current_debt:,.0f} VNĐ) không?")
                if messagebox.askyesno("Xác nhận thanh toán", msg):
                    payment_to_process = current_debt # Chỉ thanh toán bằng số nợ hiện tại
                else:
                    return # Người dùng hủy, không làm gì cả
            # --- KẾT THÚC CẢI TIẾN ---

            # 1. Cập nhật trạng thái hóa đơn thành "Đã thanh toán" (1)
            status_updated = self.model.update_invoice_status(invoice_id, 1)
            if not status_updated:
                raise Exception("Không thể cập nhật trạng thái hóa đơn.")

            # 2. Lấy debt_controller từ root_window
            debt_controller = self.view.root_window.debt_controller
            # 3. Gọi hàm update_debt của DebtController để xử lý logic công nợ
            # Hàm này sẽ tự lấy công nợ cũ, tính toán và cập nhật
            debt_controller.update_debt_on_payment(customer_id, payment_to_process)
            
            messagebox.showinfo("Thành công", f"Đã thanh toán thành công hóa đơn #{invoice_id}.")
            
            # 4. Yêu cầu các view làm mới dữ liệu
            self.view.root_window.refresh_debt_data()
            self.view.refresh_data() # Làm mới chính trang lịch sử hóa đơn

        except Exception as e:
            messagebox.showerror("Lỗi thanh toán", f"Đã xảy ra lỗi: {e}")

    def delete_invoice(self, invoice_id, customer_id, total_amount):
        """Xử lý logic xóa hóa đơn và cập nhật lại công nợ."""
        try:
            # 1. Lấy thông tin công nợ hiện tại để hiển thị trong thông báo
            current_debt, _ = self.model.get_customer_current_debt(customer_id)

            # 2. Hiển thị thông báo xác nhận chi tiết
            msg = (f"Bạn có chắc chắn muốn XÓA vĩnh viễn hóa đơn (trị giá {total_amount:,.0f} VNĐ)?\n\n"
                   f"Hành động này sẽ trừ {total_amount:,.0f} VNĐ khỏi công nợ hiện tại ({current_debt:,.0f} VNĐ) của khách hàng.")
            
            if not messagebox.askyesno("Xác nhận xóa hóa đơn", msg):
                return # Người dùng hủy

            # 3. Gọi model để xóa hóa đơn và các chi tiết liên quan
            deleted = self.model.delete_invoice_by_id(invoice_id)
            if not deleted:
                raise Exception("Không thể xóa hóa đơn khỏi cơ sở dữ liệu.")

            # 4. Gọi DebtController để cập nhật (trừ đi) công nợ
            debt_controller = self.view.root_window.debt_controller
            debt_controller.reverse_debt_on_invoice_deletion(customer_id, total_amount)

            messagebox.showinfo("Thành công", f"Đã xóa thành công hóa đơn #{invoice_id}.")

            # 5. Làm mới lại tất cả dữ liệu liên quan
            self.view.root_window.refresh_debt_data()
            self.view.refresh_data()

        except Exception as e:
            messagebox.showerror("Lỗi xóa hóa đơn", f"Đã xảy ra lỗi: {e}")


    # def load_invoice_history(self): # Hàm này có thể giữ lại hoặc bỏ đi nếu không dùng
    #     invoices = self.model.get_all_invoices_history()
    #     self.view.display_invoices(invoices, 'khach_hang')