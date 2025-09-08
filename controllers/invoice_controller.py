import tkinter as tk
from models.products_model import ProductModel
from models.invoice_model import InvoiceModel

class InvoiceController:
    def __init__(self, view, db_path):
        self.view = view
        self.model = InvoiceModel(db_path)
        self.load_invoices()

    def load_invoices(self):
        """Load invoices from the model and update the view."""
        invoices = self.model.get_all_invoices()
        self.view.update_invoice_list(invoices)

    # def create_invoice(code, customer, amount):
    #     invoice = Invoice(code, customer, float(amount))
    #     print("Hóa đơn được tạo:")
    #     print(f" - Mã: {invoice.code}")
    #     print(f" - Khách: {invoice.customer}")
    #     print(f" - Số tiền: {invoice.amount}")