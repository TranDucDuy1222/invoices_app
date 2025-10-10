import tkinter as tk
from models.invoice_model import InvoiceModel
from datetime import datetime
from tkinter import messagebox

class InvoiceController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = InvoiceModel(db_path)
        self.load_products_invoice()
        self.load_customers_invoice()
        self.load_cars_invoice()


    def load_products_invoice(self):
        products = self.model.get_all_products_and_yard()
        self.view.update_product_list(products)

    def load_customers_invoice(self):
        customers = self.model.get_all_customers_invoice()
        self.view.update_customer_list(customers)

    def load_cars_invoice(self):
        cars = self.model.get_all_cars()
        self.view.update_car_list(cars)

    def refresh_data(self):
        """Tải lại toàn bộ dữ liệu (sản phẩm, khách hàng, xe) cho trang tạo hóa đơn."""
        self.load_products_invoice()
        self.load_customers_invoice()
        self.load_cars_invoice()

    def create_invoice(self, id_kh, ngay_mua, tong_tien, trang_thai, items):
        """
        Xử lý logic tạo hóa đơn, bao gồm lưu vào DB và cập nhật công nợ.
        """
        try:
            # Chuyển đổi trạng thái
            trang_thai_db = 1 if trang_thai == "Đã thanh toán" else 0
            ngay_tao_hd = datetime.now()

            # 1. Lưu hóa đơn và chi tiết hóa đơn
            id_hd = self.model.create_invoice(id_kh, ngay_tao_hd, ngay_mua, tong_tien, trang_thai_db, items)

            # 2. Xử lý công nợ nếu "Chưa thanh toán"
            if trang_thai_db == 0:
                # Kiểm tra xem khách hàng đã có công nợ chưa
                debt_record = self.model.get_debt_by_customer_id(id_kh)
                ngay_cap_nhat = ngay_tao_hd.strftime('%d/%m/%Y %H:%M')

                if debt_record:
                    # Nếu có, cập nhật công nợ
                    id_cn = debt_record[0]
                    cong_no_cu = debt_record[4] # tong_cong_no của lần trước
                    tong_cong_no_moi = cong_no_cu + tong_tien
                    
                    # Khi tạo hóa đơn mới, không có thanh toán nào được thực hiện cho công nợ này
                    cong_no_dtt = 0 

                    self.model.update_customer_debt(id_cn, cong_no_cu, cong_no_dtt, tong_cong_no_moi, ngay_cap_nhat)
                else:
                    # Nếu chưa, tạo bản ghi công nợ mới
                    # Khi tạo mới, công nợ cũ và đã thanh toán là 0
                    cong_no_cu = 0
                    cong_no_dtt = 0
                    tong_cong_no = tong_tien # Tổng nợ ban đầu chính là tổng tiền hóa đơn
                    self.model.create_customer_debt(id_kh, cong_no_cu, cong_no_dtt, tong_cong_no, ngay_cap_nhat)

            messagebox.showinfo("Thành công", f"Đã tạo thành công hóa đơn #{id_hd}.")

            # Yêu cầu các view khác làm mới dữ liệu
            self.view.root_window.refresh_debt_data()
            self.view.root_window.refresh_invoice_history()

            return True, f"Đã tạo thành công hóa đơn #{id_hd}."

        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi tạo hóa đơn: {e}")
            return False, str(e)

    def __del__(self):
        if self.model:
            self.model.close()