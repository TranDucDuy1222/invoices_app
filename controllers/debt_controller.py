from models.debt_model import DebtModel
from datetime import datetime
from tkinter import messagebox

class DebtController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = DebtModel(db_path)
        self.view.controller = self
        self.load_debts()

    # Hàm tải danh sách công nợ
    def load_debts(self, keep_selection=False):
        """Load debts from the model and update the view."""
        selected_id = None
        if keep_selection and self.view and self.view.tree_cn.selection():
            selected_id = self.view.tree_cn.selection()[0]

        debts = self.model.get_debts()
        self.view.load_debt_data(debts)

        if selected_id and self.view:
            self.view.tree_cn.selection_set(selected_id)

    # Hàm cập nhật công nợ
    def update_debt_from_view(self, debt_id, payment_amount, payment_date=None, new_total_debt=None):
        """ Xử lý logic cập nhật công nợ theo quy trình mới. """
        try:
            # 1. Lấy thông tin công nợ hiện tại từ DB
            current_debt_record = self.model.get_by_id(debt_id)
            if not current_debt_record:
                messagebox.showerror("Lỗi", "Không tìm thấy thông tin công nợ.")
                return
            
            # Cấu trúc tuple: (id_cn, id_kh, cong_no_cu, cong_no_dtt, tong_cong_no, ngay_cap_nhat)
            # Công nợ trước khi thanh toán chính là `tong_cong_no` của lần cập nhật trước.
            debt_before_payment = current_debt_record[4]

            # 2. Tính toán các giá trị mới
            # Nếu new_total_debt được cung cấp (chế độ sửa tất cả), sử dụng nó
            if new_total_debt is not None:
                new_cong_no_cu = debt_before_payment # Nợ cũ vẫn là tổng nợ trước đó
                new_cong_no_ht = new_total_debt # Nợ mới là giá trị nhập vào
            else:
                # Nếu không, tính toán như bình thường
                new_cong_no_cu = debt_before_payment
                new_cong_no_ht = debt_before_payment - payment_amount

            if payment_date:
                # Lấy ngày từ payment_date và kết hợp với giờ phút giây hiện tại
                update_date = datetime.now().replace(
                    year=payment_date.year,
                    month=payment_date.month,
                    day=payment_date.day
                ).strftime('%d/%m/%Y %H:%M')
            else:
                # Nếu không, lấy ngày giờ hiện tại
                update_date = datetime.now().strftime('%d/%m/%Y %H:%M')

            # Chỉ kiểm tra nếu không ở chế độ sửa tất cả
            if new_total_debt is None:
                if payment_amount > debt_before_payment:
                    messagebox.showerror("Lỗi", f"Số tiền thanh toán ({payment_amount:,.0f} VNĐ) không được lớn hơn công nợ hiện tại ({debt_before_payment:,.0f} VNĐ).")
                    return False

            # 4. Gọi model để cập nhật DB với các giá trị mới
            self.model.update(debt_id, new_cong_no_cu, payment_amount, new_cong_no_ht, update_date)

            messagebox.showinfo("Thành công", "Đã cập nhật công nợ thành công!")

            # Tải lại dữ liệu Treeview và giữ nguyên lựa chọn
            self.load_debts(keep_selection=True)

            # Yêu cầu view chuyển sang chế độ "Sửa tất cả" sau một khoảng trễ nhỏ
            # để đảm bảo nó chạy sau khi sự kiện on_select đã xử lý xong.
            self.view.schedule_enter_full_edit_mode()

            return True

        except Exception as e:
            messagebox.showerror("Lỗi cập nhật", f"Đã xảy ra lỗi khi cập nhật công nợ: {e}")
            return False

    def update_debt_on_payment(self, customer_id, paid_amount):
        """
        Cập nhật công nợ khi một hóa đơn được thanh toán.
        Hàm này được gọi từ InvoiceHistoryController.
        """
        try:
            # 1. Lấy bản ghi công nợ gần nhất của khách hàng
            debt_record = self.model.get_by_customer_id(customer_id)
            if not debt_record:
                # Trường hợp này hiếm khi xảy ra nếu logic tạo hóa đơn đúng
                print(f"Không tìm thấy công nợ cho khách hàng ID: {customer_id}. Bỏ qua cập nhật công nợ.")
                return

            id_cn, _, _, _, current_total_debt, _ = debt_record

            # 2. Tính toán các giá trị mới
            new_cong_no_cu = current_total_debt # Nợ cũ là tổng nợ hiện tại
            new_total_debt = current_total_debt - paid_amount # Nợ mới = nợ cũ - đã thanh toán
            update_date = datetime.now().strftime('%d/%m/%Y %H:%M')

            # 3. Gọi model để cập nhật
            self.model.update(id_cn, new_cong_no_cu, paid_amount, new_total_debt, update_date)

        except Exception as e:
            # Lỗi này sẽ không hiển thị messagebox để tránh làm phiền người dùng 2 lần
            print(f"Lỗi ngầm khi cập nhật công nợ từ thanh toán hóa đơn: {e}")
            raise e # Ném lỗi ra để hàm pay_invoice có thể bắt và xử lý

    def reverse_debt_on_invoice_deletion(self, customer_id, deleted_invoice_amount):
        """
        Cập nhật (trừ đi) công nợ khi một hóa đơn bị xóa.
        """
        try:
            # 1. Lấy bản ghi công nợ gần nhất của khách hàng
            debt_record = self.model.get_by_customer_id(customer_id)
            if not debt_record:
                print(f"Không tìm thấy công nợ cho khách hàng ID: {customer_id} để hoàn trả. Bỏ qua.")
                return

            id_cn, _, _, _, current_total_debt, _ = debt_record

            # --- CẢI TIẾN: Xử lý trường hợp công nợ nhỏ hơn giá trị hóa đơn bị xóa ---
            amount_to_reverse = deleted_invoice_amount
            if current_total_debt < deleted_invoice_amount:
                # Nếu công nợ hiện tại nhỏ hơn, chỉ hoàn trả một lượng bằng công nợ hiện tại để đưa nợ về 0
                amount_to_reverse = current_total_debt

            # 2. Tính toán các giá trị mới
            new_cong_no_cu = current_total_debt # Nợ cũ là tổng nợ hiện tại
            # Nợ mới = nợ hiện tại - số tiền của hóa đơn bị xóa
            new_total_debt = current_total_debt - amount_to_reverse
            update_date = datetime.now().strftime('%d/%m/%Y %H:%M')

            # 3. Gọi model để cập nhật. Số tiền thanh toán (cong_no_dtt) sẽ là số âm để thể hiện đây là một giao dịch đảo ngược.
            self.model.update(id_cn, new_cong_no_cu, amount_to_reverse, new_total_debt, update_date)

        except Exception as e:
            print(f"Lỗi ngầm khi hoàn trả công nợ từ xóa hóa đơn: {e}")
            raise e

    def __del__(self):
        self.model.close()