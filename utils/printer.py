import os
import tempfile
import logging
import subprocess
import time
import win32print
import winreg # Thêm thư viện để đọc Windows Registry
from datetime import datetime

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class InvoicePrinter:
    def __init__(self, printer_name=None): # Để printer_name là None để mặc định lấy máy in mặc định
        self.printer_name = printer_name
        self.pagesize = landscape(A4) # <-- THAY ĐỔI: Sử dụng khổ giấy ngang
        self.width, self.height = self.pagesize
        self.margin = 15 * mm # Giảm lề một chút để có thêm không gian

        # Đăng ký font hỗ trợ Unicode (ví dụ: DejaVuSans)
        # Bạn cần tải file font DejaVuSans.ttf và đặt vào thư mục dự án (ví dụ: trong thư mục 'fonts')
        try:
            pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/dejavuFonts/ttf/DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/dejavuFonts/ttf/DejaVuSans-Bold.ttf'))
            self.font_name = 'DejaVuSans'
            self.font_name_bold = 'DejaVuSans-Bold'
        except Exception as e:
            logging.warning(f"Không thể tải font DejaVu. Sử dụng font mặc định. Lỗi: {e}")
            self.font_name = 'Helvetica'
            self.font_name_bold = 'Helvetica-Bold'

    def _draw_header(self, c, invoice_data):
        # Bắt đầu từ trên cùng
        y = self.height - self.margin

        # ===== Thông tin công ty =====
        c.setFont(self.font_name_bold, 12)
        c.drawString(self.margin, y, "Công ty TNHH TM DV Tính Khang Phúc")
        y -= 6*mm
        c.setFont(self.font_name_bold, 10)
        c.drawString(self.margin, y, "Chuyên kinh doanh & vận chuyển: cát, đất, đá, sỏi và san lấp mặt bằng")
        y -= 5*mm
        c.setFont(self.font_name, 10)
        c.drawString(self.margin, y, "MST: 0314412607")
        y -= 5*mm
        c.drawString(self.margin, y, "Địa chỉ: 149A, Lý Thế Kiệt, P. Linh Đông, Q. Thủ Đức, TP.HCM")
        y -= 5*mm
        c.drawString(self.margin, y, "Liên hệ: 0977.209.709 (Đạt) - 0967.209.709 (Trinh)")

        # ===== Tiêu đề chính =====
        y -= 10*mm
        c.setFont(self.font_name_bold, 18)
        c.drawCentredString(self.width / 2, y, "Bảng Kê Khối Lượng")

        # ===== Frame thông tin khách hàng =====
        y -= 12*mm
        c.setFont(self.font_name_bold, 10)
        c.drawString(self.margin, y, f"Tên khách hàng: {invoice_data['customer_name']}")
        y -= 5*mm
        c.setFont(self.font_name, 10)
        c.drawString(self.margin, y, f"Số điện thoại: {invoice_data['customer_phone']}")
        y -= 5*mm
        c.drawString(self.margin, y, f"Địa chỉ khách hàng: {invoice_data['customer_address']}")

        # ===== Frame thông tin ngày tháng =====
        c.drawRightString(self.width - self.margin, y + 10*mm, f"Ngày lập: {invoice_data['invoice_date']}")
        c.drawRightString(self.width - self.margin, y + 5*mm, f"Ngày in: {datetime.now().strftime('%d/%m/%Y')}")

    def _draw_footer(self, c, invoice_data):
        # Lấy vị trí y hiện tại của con trỏ, đây sẽ là vị trí cuối cùng của bảng
        y_pos = c.getY()
        
        # Vẽ footer ngay bên dưới bảng với một khoảng cách nhỏ
        y_footer_start = y_pos - 15*mm
        c.setFont(self.font_name_bold, 11)
        c.drawRightString(self.width - self.margin, y_footer_start, f"Tổng tiền hóa đơn: {invoice_data['total_invoice']}")
        c.drawRightString(self.width - self.margin, y_footer_start - 5*mm, f"Công nợ hiện tại: {invoice_data['current_debt']}")

        c.setFont(self.font_name, 10)
        c.drawCentredString(self.width * 0.2, y_footer_start - 20*mm, "Người mua hàng")
        c.drawCentredString(self.width * 0.8, y_footer_start - 20*mm, "Người bán hàng")

    def create_invoice_pdf(self, invoice_data, items):
        # Tạo một file tạm thời để lưu PDF
        fd, filepath = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        logging.info(f"Tạo file PDF tạm thời tại: {filepath}")

        c = canvas.Canvas(filepath, pagesize=self.pagesize)

        # --- Tính toán layout ---
        header_height = 55 * mm
        footer_height = 30 * mm # Giảm chiều cao ước tính của footer
        row_height = 8 * mm
        table_header_height = 10 * mm

        available_height_first_page = self.height - self.margin - self.margin - header_height - footer_height
        available_height_next_pages = self.height - self.margin - self.margin - (15*mm) - footer_height # 15mm cho header trang tiếp theo

        items_per_first_page = int((available_height_first_page - table_header_height) / row_height)
        items_per_next_page = int((available_height_next_pages - table_header_height) / row_height)

        # --- Dữ liệu bảng ---
        table_data = [["Ngày mua", "Mặt hàng", "Số xe", "Bãi", "ĐV", "SL", "Thành tiền", "Nơi giao"]]
        for item in items:
            # item: (ngay_mua, ten_sp, so_xe, lay_tai_bai, don_vi, so_luong, thanh_tien, noi_giao)
            ngay_mua = item[0]
            ten_sp = item[1]
            so_xe = item[2]
            lay_tai_bai = item[3]
            don_vi = item[4]
            so_luong = str(item[5])
            thanh_tien = f"{int(item[6]):,.0f}".replace(",", ".")
            noi_giao = item[7]
            table_data.append([ngay_mua, ten_sp, so_xe, lay_tai_bai, don_vi, so_luong, thanh_tien, noi_giao])

        # --- Vẽ các trang ---
        item_index = 0
        page_num = 1

        while item_index < len(items):
            if page_num > 1:
                c.showPage() # Bắt đầu trang mới

            # Vẽ header cho trang đầu tiên
            if page_num == 1:
                self._draw_header(c, invoice_data)
                y_start = self.height - self.margin - header_height
                items_to_draw_count = items_per_first_page
            else:
                # Header đơn giản cho các trang tiếp theo
                c.setFont(self.font_name, 9)
                c.drawString(self.margin, self.height - self.margin, f"Hóa đơn (tiếp theo) - Trang {page_num}")
                y_start = self.height - self.margin
                items_to_draw_count = items_per_next_page

            # Lấy phần dữ liệu cho trang hiện tại
            end_index = min(item_index + items_to_draw_count, len(items))
            current_page_items_data = table_data[0:1] + table_data[item_index + 1 : end_index + 1]

            # Tạo bảng
            # Tăng độ rộng các cột để tận dụng không gian ngang
            col_widths = [25*mm, 60*mm, 25*mm, 30*mm, 15*mm, 15*mm, 30*mm, 60*mm]
            table = Table(current_page_items_data, colWidths=col_widths)
            style = TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), self.font_name_bold),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (4, 1), (5, -1), 'CENTER'), # Căn giữa cột ĐV, SL
                ('ALIGN', (6, 1), (6, -1), 'RIGHT'),  # Căn phải cột Thành tiền
                ('FONTNAME', (0, 1), (-1, -1), self.font_name),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            table.setStyle(style)

            # Tính toán vị trí và vẽ bảng
            table_width, table_height = table.wrapOn(c, self.width, self.height)
            table.drawOn(c, self.margin, y_start - table_height)
            
            # Vẽ footer nếu đây là trang cuối cùng
            if end_index == len(items):
                self._draw_footer(c, invoice_data)

            # Cập nhật chỉ số
            item_index = end_index
            page_num += 1

        c.save()
        logging.info("Đã tạo xong file PDF.")
        return filepath

    def _find_pdf_print_command(self):
        """
        Tìm lệnh in PDF từ Windows Registry.
        Trả về một tuple (command_template, use_printer_name)
        """
        try:
            # Tìm ProgID cho file .pdf
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'.pdf', 0, winreg.KEY_READ) as key:
                prog_id = winreg.QueryValue(key, None)

            # Log chương trình dùng để mở file PDF
            try:
                open_cmd_path = rf'{prog_id}\shell\open\command'
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, open_cmd_path, 0, winreg.KEY_READ) as open_key:
                    open_cmd = winreg.QueryValue(open_key, None)
                    logging.info(f"Chương trình mặc định để MỞ file PDF: {open_cmd}")
            except FileNotFoundError:
                logging.warning("Không tìm thấy lệnh 'open' trong registry cho file PDF.")
            except Exception as e:
                logging.error(f"Lỗi khi tìm lệnh 'open' trong registry: {e}")

            # Thử tìm lệnh "printto" trước (linh hoạt hơn)
            cmd_path = rf'{prog_id}\shell\printto\command'
            # Thêm các tham số cho OpenKey để tránh lỗi Access is denied trên một số hệ thống
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, cmd_path, 0, winreg.KEY_READ) as key:
                cmd_template = winreg.QueryValue(key, None)
                # Lệnh printto thường có dạng: "C:\path\to\AcroRd32.exe" /t "%1" "%2"
                # %1 là file, %2 là tên máy in
                logging.info(f"Tìm thấy lệnh 'printto' trong registry: {cmd_template}")
                return (cmd_template, True)

        except FileNotFoundError:
            # Nếu không có 'printto', thử tìm lệnh 'print'
            try:
                cmd_path = rf'{prog_id}\shell\print\command'
                with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, cmd_path, 0, winreg.KEY_READ) as key:
                    cmd_template = winreg.QueryValue(key, None)
                    # Lệnh print thường có dạng: "C:\path\to\AcroRd32.exe" /p "%1"
                    logging.info(f"Tìm thấy lệnh 'print' trong registry: {cmd_template}")
                    return (cmd_template, False)
            except FileNotFoundError:
                logging.warning("Không tìm thấy lệnh 'print' hoặc 'printto' trong registry cho file PDF.")
                return (None, False)
        except Exception as e:
            logging.error(f"Lỗi khi truy vấn registry: {e}")
            return (None, False)

    def print_file(self, filepath):
        # Bỏ khối try...finally ở đây để di chuyển logic xóa file
            # Xác định máy in sẽ sử dụng
            current_printer = self.printer_name or win32print.GetDefaultPrinter()
            logging.info(f"Lệnh sẽ được gửi đến máy in mặc định của hệ thống: {current_printer}")

            # --- Ưu tiên 1: Thử dùng os.startfile ---
            logging.info(f"Ưu tiên 1: Thử dùng os.startfile để in file: {filepath}")
            try:
                os.startfile(filepath, "print")
                logging.info("Đã gửi lệnh in qua os.startfile thành công. Vui lòng đợi máy in xử lý.")
                time.sleep(10) # Đợi để hệ thống xử lý
                return True
            except OSError as e:
                if e.winerror == 1155: # Lỗi "No application is associated"
                    logging.warning("os.startfile thất bại (WinError 1155). Chuyển sang phương án 2.")
                    # --- Ưu tiên 2: Tìm trong Registry và dùng subprocess ---
                    cmd_template, use_printer_name = self._find_pdf_print_command()
                    if cmd_template:
                        if use_printer_name:
                            # Lệnh printto: thay thế %1 bằng file, %2 bằng máy in
                            command = cmd_template.replace('"%1"', f'"{filepath}"').replace('"%2"', f'"{current_printer}"')
                        else:
                            # Lệnh print: chỉ thay thế %1 bằng file
                            command = cmd_template.replace('"%1"', f'"{filepath}"')

                        logging.info(f"Ưu tiên 2: Thực thi lệnh từ registry: {command}")
                        subprocess.run(command, shell=True, check=True)
                        logging.info("Đã gửi lệnh in qua subprocess thành công.")
                        time.sleep(10)
                        return True
                # Nếu là lỗi khác, báo lỗi luôn
                logging.error(f"Lỗi OSError không xác định khi gọi os.startfile: {e}", exc_info=True)
                return False
            except Exception as e:
                logging.error(f"Lỗi không xác định trong print_file: {e}", exc_info=True)
                return False


    def print_invoice(self, invoice_data, items):
        """
        Hàm chính để tạo và in hóa đơn.
        """
        if not items:
            logging.warning("Không có mặt hàng nào để in.")
            return False, "Không có mặt hàng nào để in."
        
        pdf_path = None
        try:
            # 1. Tạo file PDF
            pdf_path = self.create_invoice_pdf(invoice_data, items)
            if pdf_path:
                # 2. Thử in file
                if self.print_file(pdf_path):
                    # 3. Nếu in thành công, trả về True
                    return True, "Đã gửi hóa đơn đến máy in."
                else:
                    # 4. Nếu in thất bại, mở file cho người dùng tự in
                    try:
                        logging.info(f"Đang mở file PDF để bạn có thể in thủ công: {pdf_path}")
                        os.startfile(pdf_path)
                    except Exception as open_error:
                        logging.error(f"Không thể tự động mở file PDF. Lỗi: {open_error}")
                    return False, f"Không thể gửi file đến máy in. Vui lòng kiểm tra file tại: {pdf_path}"
            else:
                return False, "Tạo file PDF thất bại."
        except Exception as e:
            # Lỗi này sẽ bắt các lỗi nghiêm trọng hơn, ví dụ như từ create_invoice_pdf
            logging.error(f"Lỗi trong quá trình in hóa đơn: {e}", exc_info=True)
            return False, f"Lỗi: {e}"
        finally:
            # 5. Chỉ xóa file nếu nó đã được tạo và quá trình in thành công
            # (Trong trường hợp này, chúng ta sẽ để file lại nếu in thất bại để người dùng kiểm tra)
            pass # Tạm thời không xóa gì cả để đảm bảo an toàn
