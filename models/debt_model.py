from .base_model import BaseModel
import sqlite3

class DebtModel(BaseModel):
    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def get_debts(self):
        """Lấy danh sách công nợ kèm tên khách hàng từ database"""
        sql = """
            SELECT 
                d.id_cn,
                c.ten,
                d.cong_no_cu,
                d.cong_no_dtt,
                d.tong_cong_no,
                d.ngay_cap_nhat
            FROM debts d
            JOIN customers c ON d.id_kh = c.id_kh
            ORDER BY c.ten
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_by_id(self, debt_id):
        """ Lấy một bản ghi công nợ bằng id_cn. """
        query = "SELECT * FROM debts WHERE id_cn = ?"
        self.cursor.execute(query, (debt_id,))
        return self.cursor.fetchone()

    def get_by_customer_id(self, customer_id):
        """ Lấy bản ghi công nợ gần nhất bằng id_kh. """
        query = "SELECT * FROM debts WHERE id_kh = ? ORDER BY ngay_cap_nhat DESC LIMIT 1"
        self.cursor.execute(query, (customer_id,))
        return self.cursor.fetchone()

    def update(self, debt_id, new_cong_no_cu, payment_amount, new_cong_no_ht, update_date):
        """
        Cập nhật thông tin công nợ cho một bản ghi.
        - Cập nhật công nợ cũ (`cong_no_cu`) bằng công nợ hiện tại trước khi thanh toán.
        - Cập nhật số tiền đã thanh toán (`cong_no_dtt`).
        - Cập nhật công nợ hiện tại/còn lại (`tong_cong_no`).
        """
        query = """
            UPDATE debts
            SET cong_no_cu = ?,
                cong_no_dtt = ?,
                tong_cong_no = ?,
                ngay_cap_nhat = ?
            WHERE id_cn = ?
        """
        try:
            self.cursor.execute(query, (new_cong_no_cu, payment_amount, new_cong_no_ht, update_date, debt_id))
            self.connection.commit()
        except sqlite3.Error as e:
            self.connection.rollback()
            raise e


    def close(self):
        if hasattr(self, 'connection'):
            self.connection.close()