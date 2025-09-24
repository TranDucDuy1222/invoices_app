from .base_model import BaseModel
import sqlite3
from datetime import datetime

class InvoiceHistoryModel(BaseModel):
    def __init__(self, db_path):
        # Gọi __init__ của lớp cha (BaseModel) để có self.conn và self.cursor
        super().__init__(db_path)

    def get_invoices_by_status(self, status):
        """
        Lấy danh sách hóa đơn dựa trên trạng thái (0: Chưa thanh toán, 1: Đã thanh toán).
        """
        # status: 0 for unpaid, 1 for paid
        query = """
            SELECT
                i.id_hd,
                i.ngay_tao_hd,
                c.ten,
                a.dia_chi,
                c.sdt,
                i.tong_tien,
                CASE i.trang_thai
                    WHEN 1 THEN 'Đã thanh toán'
                    ELSE 'Chưa thanh toán'
                END AS trang_thai_text,
                c.id_kh
            FROM invoices i
            JOIN customers c ON i.id_kh = c.id_kh
            LEFT JOIN addresses a ON c.id_kh = a.id_kh
            WHERE i.trang_thai = ?
            ORDER BY i.id_hd DESC;
        """
        try:
            self.cursor.execute(query, (status,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi truy vấn hóa đơn: {e}")
            return []

    def get_summary_invoices_by_date_range(self, start_date, end_date):
        """
        Lấy danh sách hóa đơn chưa thanh toán được gộp theo khách hàng trong một khoảng ngày.
        """
        query = """
            SELECT
                c.id_kh,
                ? || ' -> ' || ? as ngay_gop, -- Hiển thị khoảng ngày
                c.ten,
                a.dia_chi,
                c.sdt,
                SUM(i.tong_tien) as tong_tien_gop,
                'Hóa đơn theo tuần' as trang_thai,
                c.id_kh -- Thêm id_kh vào cuối để cấu trúc tuple nhất quán
            FROM invoices i
            JOIN customers c ON i.id_kh = c.id_kh
            LEFT JOIN addresses a ON c.id_kh = a.id_kh
            WHERE i.trang_thai = 0 AND date(substr(i.ngay_mua, 7, 4) || '-' || substr(i.ngay_mua, 4, 2) || '-' || substr(i.ngay_mua, 1, 2)) BETWEEN date(?) AND date(?)
            GROUP BY c.id_kh, c.ten, a.dia_chi, c.sdt
            ORDER BY c.ten;
        """
        try:
            self.cursor.execute(query, (start_date.strftime('%d/%m'), end_date.strftime('%d/%m/%Y'), start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi truy vấn hóa đơn theo tuần: {e}")
            return []

    # Lấy chi tiết các mặt hàng của một hóa đơn cụ thể
    def get_invoice_details(self, invoice_id):
        """Lấy chi tiết các mặt hàng của một hóa đơn cụ thể."""
        query = """
            SELECT 
                i.ngay_mua, 
                p.ten_sp, 
                id.so_luong, 
                id.thanh_tien, -- Lấy thẳng thành tiền của chi tiết hóa đơn
                id.noi_giao,
                cr.bien_so,
                y.ten_bai,
                id.don_vi_tinh
            FROM invoice_details id
            JOIN products p ON id.id_sp = p.id_sp
            JOIN invoices i ON id.id_hd = i.id_hd
            LEFT JOIN cars cr ON id.id_xe = cr.id_car
            LEFT JOIN yards y ON id.id_bai = y.id_bai
            WHERE id.id_hd = ?;
        """
        self.cursor.execute(query, (invoice_id,))
        return self.cursor.fetchall()

    # Lấy tổng công nợ hiện tại của một khách hàng
    def get_customer_current_debt(self, customer_id):
        """Lấy tổng công nợ hiện tại của một khách hàng từ bảng debts."""
        query = "SELECT tong_cong_no, cong_no_cu FROM debts WHERE id_kh = ? ORDER BY ngay_cap_nhat DESC LIMIT 1"
        try:
            self.cursor.execute(query, (customer_id,))
            result = self.cursor.fetchone()
            return result if result else (0, 0) # Trả về một tuple (tong_cong_no, cong_no_cu)
        except Exception as e:
            print(f"Lỗi khi truy vấn công nợ khách hàng: {e}")
            return (0, 0)

    # Lấy tất cả các mặt hàng trong các hóa đơn chưa thanh toán của một khách hàng
    def get_unpaid_items_by_customer_and_date(self, customer_id, start_date, end_date):
        """Lấy tất cả các mặt hàng trong các hóa đơn chưa thanh toán của một khách hàng trong một khoảng ngày."""
        query = """
            SELECT
                i.ngay_mua,
                p.ten_sp,
                id.so_luong,
                id.thanh_tien,
                id.noi_giao,
                cr.bien_so,
                y.ten_bai,
                id.don_vi_tinh
            FROM invoice_details id
            JOIN products p ON id.id_sp = p.id_sp
            JOIN invoices i ON id.id_hd = i.id_hd
            LEFT JOIN cars cr ON id.id_xe = cr.id_car
            LEFT JOIN yards y ON id.id_bai = y.id_bai
            WHERE i.id_kh = ? AND i.trang_thai = 0 AND date(substr(i.ngay_mua, 7, 4) || '-' || substr(i.ngay_mua, 4, 2) || '-' || substr(i.ngay_mua, 1, 2)) BETWEEN date(?) AND date(?)
            ORDER BY i.ngay_mua;
        """
        try:
            self.cursor.execute(query, (customer_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Lỗi khi truy vấn các mặt hàng chưa thanh toán: {e}")
            return []

    def update_invoice_status(self, invoice_id, new_status):
        """Cập nhật trạng thái của một hóa đơn."""
        query = "UPDATE invoices SET trang_thai = ? WHERE id_hd = ?"
        try:
            self.cursor.execute(query, (new_status, invoice_id))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Lỗi khi cập nhật trạng thái hóa đơn: {e}")
            return False