from models.setting_model import SettingModel
from views.config import db_path
from tkinter import messagebox

class SettingController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = SettingModel(db_path)
        self.view.controller = self

    def delete_data_by_date(self, tables_to_delete, start_date, end_date):
        """Xử lý yêu cầu xóa dữ liệu theo khoảng ngày."""
        if not tables_to_delete:
            messagebox.showwarning("Chưa chọn bảng", "Vui lòng chọn ít nhất một loại dữ liệu để xóa.")
            return

        # Chỉ các bảng có cột ngày mới có thể xóa theo ngày
        valid_tables = [t for t in tables_to_delete if t in ['invoices', 'debts']]
        if not valid_tables:
            messagebox.showwarning("Không hợp lệ", "Các loại dữ liệu bạn chọn không hỗ trợ xóa theo ngày.")
            return

        success, result = self.model.delete_data_in_date_range(valid_tables, start_date, end_date)

        if success:
            deleted_counts = result
            report = "\n".join([f"- {key}: {value} dòng" for key, value in deleted_counts.items()])
            messagebox.showinfo("Hoàn thành", f"Đã xóa dữ liệu thành công:\n{report}")
        else:
            messagebox.showerror("Lỗi", f"Xóa dữ liệu thất bại: {result}")

    def delete_all_data(self, tables_to_delete):
        """Xử lý yêu cầu xóa toàn bộ dữ liệu."""
        if not tables_to_delete:
            messagebox.showwarning("Chưa chọn bảng", "Vui lòng chọn ít nhất một loại dữ liệu để xóa.")
            return

        success, message = self.model.delete_all_data_from_tables(tables_to_delete)
        if success:
            messagebox.showinfo("Hoàn thành", message)
        else:
            messagebox.showerror("Lỗi", f"Xóa dữ liệu thất bại: {message}")
