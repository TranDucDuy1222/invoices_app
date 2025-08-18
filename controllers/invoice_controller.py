from models.invoice import Invoice
import tkinter as tk

def create_invoice(code, customer, amount):
    invoice = Invoice(code, customer, float(amount))
    print("Hóa đơn được tạo:")
    print(f" - Mã: {invoice.code}")
    print(f" - Khách: {invoice.customer}")
    print(f" - Số tiền: {invoice.amount}")