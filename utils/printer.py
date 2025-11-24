import os
import sys
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

def resource_path(relative_path):
    """ Lấy đường dẫn tuyệt đối đến tài nguyên, hoạt động cho cả chế độ dev và PyInstaller """
    try:
        # PyInstaller tạo một thư mục tạm thời và lưu đường dẫn trong _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Nếu không phải PyInstaller, dùng đường dẫn thông thường
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class InvoicePrinter:
    def __init__(self, printer_name=None):
        """
        Hàm khởi tạo đã được điều chỉnh để hoạt động với PyInstaller.
        """
        self.printer_name = printer_name
        self.pagesize = landscape(A4)
        self.width, self.height = self.pagesize
        self.margin = 15 * mm

        try:
            # Lấy đường dẫn đến thư mục Fonts của Windows
            font_dir = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Fonts")

            # Đường dẫn đầy đủ đến các file font Times New Roman
            font_regular_path = os.path.join(font_dir, 'times.ttf')
            font_bold_path = os.path.join(font_dir, 'timesbd.ttf')

            # Đăng ký các font này với ReportLab
            pdfmetrics.registerFont(TTFont('TimesNewRoman', font_regular_path))
            pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', font_bold_path))

            # Sử dụng các font vừa đăng ký
            self.font_name = 'TimesNewRoman'
            self.font_name_bold = 'TimesNewRoman-Bold'
            logging.info("Đã tải thành công font Times New Roman từ hệ thống Windows để hỗ trợ tiếng Việt.")

        except Exception as e:
            # Nếu không tìm thấy font của Windows, quay lại dùng font mặc định (có thể bị lỗi ô đen)
            logging.warning(f"Không thể tải font Times New Roman từ hệ thống. Sử dụng font mặc định. Lỗi: {e}")
            self.font_name = 'Helvetica'
            self.font_name_bold = 'Helvetica-Bold'
            logging.warning("Lưu ý: Font mặc định có thể không hỗ trợ đầy đủ tiếng Việt.")

    def _draw_header(self, c, invoice_data):
        # Bắt đầu từ trên cùng
        y = self.height - self.margin

        # ===== Thông tin công ty =====
        c.setFont(self.font_name_bold, 16)
        c.drawString(self.margin, y, "Công ty TNHH TM DV Tính Khang Phúc")
        y -= 8*mm
        c.setFont(self.font_name_bold, 14)
        c.drawString(self.margin, y, "Chuyên kinh doanh & vận chuyển: cát, đất, đá, sỏi và san lấp mặt bằng")
        y -= 6*mm
        c.setFont(self.font_name, 14)
        c.drawString(self.margin, y, "MST: 0319133438")
        y -= 6*mm
        c.drawString(self.margin, y, "STK: 45366087 - Ngân hàng ACB - Tên TK: Nguyễn Thị Kiều Chinh")
        y -= 6*mm
        c.drawString(self.margin, y, "Địa chỉ: 92 Đường 24, Phường Tam Bình, TP. Hồ Chí Minh")
        y -= 6*mm
        c.drawString(self.margin, y, "Liên hệ: 0967.209.709 (Chinh) - 0977.209.709 (Đạt)")

        # ===== Tiêu đề chính =====
        y -= 10*mm
        c.setFont(self.font_name_bold, 18)
        c.drawCentredString(self.width / 2, y, "BẢNG KÊ KHỐI LƯỢNG")

        # ===== Frame thông tin khách hàng =====
        # THAY ĐỔI: Tính toán lại tọa độ Y để không bị ghi đè
        y_info_block = y - 15*mm # Tọa độ Y chung cho cả khối thông tin khách hàng và ngày tháng
        c.setFont(self.font_name_bold, 14)
        c.drawString(self.margin, y_info_block, f"Tên khách hàng: {invoice_data['customer_name']}")
        
        c.setFont(self.font_name, 14)
        c.drawString(self.margin, y_info_block - 6*mm, f"Số điện thoại: {invoice_data['customer_phone']}")
        c.drawString(self.margin, y_info_block - 12*mm, f"Địa chỉ khách hàng: {invoice_data['customer_address']}")

        # ===== Frame thông tin ngày tháng =====
        # THAY ĐỔI: Đặt lại vị trí cho khối ngày tháng để ngang hàng với thông tin khách hàng
        c.drawRightString(self.width - self.margin, y_info_block, f"Ngày lập: {invoice_data['invoice_date']}")
        c.drawRightString(self.width - self.margin, y_info_block - 6*mm, f"Ngày in: {datetime.now().strftime('%d/%m/%Y')}")

    def _draw_footer(self, c, invoice_data, table_bottom_y):
        # --- Vẽ phần tổng tiền ---
        y_footer_start = table_bottom_y - 15 * mm

        c.setFont(self.font_name_bold, 14)
        c.drawRightString(self.width - self.margin, y_footer_start, f"Tổng tiền hóa đơn: {invoice_data['total_invoice']}")
        c.drawRightString(self.width - self.margin, y_footer_start - 6 * mm, f"Công nợ kỳ trước: {invoice_data['paid_amount']}")
        c.drawRightString(self.width - self.margin, y_footer_start - 12 * mm, f"Tổng phải thu hiện tại: {invoice_data['current_debt']}")

        content_width = self.width * 0.7               # vùng nội dung chữ ký
        start_x = self.margin                          # bắt đầu từ lề trái
        col1_x = start_x + content_width * 0.20        # cột 1 (Người mua hàng)
        col2_x = start_x + content_width * 0.65        # cột 2 (Người lập phiếu)

        # --- Tọa độ dòng chữ ký ---
        y_base = y_footer_start - 30 * mm

        # --- Dòng "Ngày ... Tháng ... Năm ..." phía trên cột Người mua hàng ---
        c.setFont(self.font_name, 14)
        c.drawCentredString(col1_x, y_base + 8 * mm, "Ngày .......... Tháng .......... Năm ..........")

        # --- Dòng chữ ký chính ---
        c.setFont(self.font_name, 14)
        c.drawCentredString(col1_x, y_base, "Người lập phiếu")
        c.drawCentredString(col2_x, y_base, "Người mua hàng")


    def create_invoice_pdf(self, invoice_data, items):
        # --- CẢI TIẾN: Logic tạo đường dẫn và tên file an toàn ---
        def sanitize_filename(name):
            """Loại bỏ các ký tự không hợp lệ và chuẩn hóa tên file/thư mục."""
            # Thay thế các ký tự đặc biệt bằng gạch dưới
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                name = name.replace(char, '_')
            # Thay thế khoảng trắng bằng gạch dưới để đảm bảo tính nhất quán
            name = name.replace(' ', '_')
            # Loại bỏ các ký tự không in được và dấu tiếng Việt (để tương thích tốt hơn)
            import unicodedata
            nfkd_form = unicodedata.normalize('NFKD', name)
            return "".join([c for c in nfkd_form if not unicodedata.combining(c) and c.isprintable()]).strip()

        # 1. "Làm sạch" các thành phần của tên file
        customer_name = invoice_data.get('customer_name', 'KhachHangKhongTen')
        # Lấy công nợ, bỏ " VNĐ" và các ký tự không phải số
        current_debt_cleaned = invoice_data.get('current_debt', '0').replace(" VNĐ", "").strip()

        invoice_date_raw = invoice_data.get('invoice_date', datetime.now().strftime('%d/%m/%Y'))

        safe_customer_name = customer_name
        safe_current_debt = current_debt_cleaned
        safe_invoice_date = sanitize_filename(invoice_date_raw)

        # THÊM: Tạo một chuỗi thời gian duy nhất (Giờ-Phút-Giây) để tránh trùng lặp file
        timestamp = datetime.now().strftime("%H-%M")

        # 2. Tạo tên file và thư mục đã được "làm sạch"
        save_dir = r"C:\Bảng Kê Khối Lượng"
        os.makedirs(save_dir, exist_ok=True)
        # THAY ĐỔI: Thêm timestamp vào cuối tên file
        filename = f"{safe_customer_name}_{safe_current_debt}_{safe_invoice_date}_{timestamp}.pdf"

        # 4. Tạo đường dẫn đầy đủ
        filepath = os.path.join(save_dir, filename)
        logging.info(f"Tạo file PDF tại: {filepath}")
        # --- KẾT THÚC THAY ĐỔI ---

        c = canvas.Canvas(filepath, pagesize=self.pagesize)


        # --- Hàm tiện ích để cắt ngắn văn bản ---
        def truncate_text(text, max_width, font_name, font_size):
            """Cắt ngắn văn bản nếu nó vượt quá chiều rộng cho phép và thêm dấu '...'."""
            # Thêm một khoảng đệm nhỏ để đảm bảo không bị sát lề
            padding = 1 * mm # Tăng padding để đảm bảo vừa vặn khi căn giữa
            available_width = max_width - padding

            # Nếu văn bản vừa đủ, trả về luôn
            if pdfmetrics.stringWidth(text, font_name, font_size) <= available_width:
                return text

            # Nếu không, cắt bớt và thêm '...'
            ellipsis = '...'
            ellipsis_width = pdfmetrics.stringWidth(ellipsis, font_name, font_size)
            
            # Cắt từ cuối chuỗi cho đến khi chiều rộng phù hợp
            for i in range(len(text) - 1, 0, -1):
                truncated = text[:i]
                if pdfmetrics.stringWidth(truncated, font_name, font_size) + ellipsis_width <= available_width:
                    return truncated + ellipsis
            
            # Trường hợp chuỗi quá ngắn, chỉ trả về dấu '...'
            return ellipsis

        # --- Dữ liệu bảng ---
        # THAY ĐỔI: Sắp xếp lại tiêu đề cột theo yêu cầu mới
        table_header = ["Ngày", "Tên mặt hàng", "Số xe", "Số khối", "Số\nchuyến", "Giá tại bãi", "Phí\nvận chuyển", "Thành tiền", "Nơi giao"]
        col_widths = [25*mm, 55*mm, 25*mm, 18*mm, 24*mm, 27*mm, 26*mm, 33*mm, 32*mm]
        body_font_size = 14

        table_data = [table_header]
        for item in items:
            # item: (ngay_mua, ten_sp, so_xe, lay_tai_bai, don_vi, so_luong, thanh_tien, noi_giao, don_gia, phi_vc)
            # Áp dụng hàm truncate_text cho các cột có thể bị tràn
            ngay_mua = truncate_text(item[0], col_widths[0], self.font_name, body_font_size)
            ten_sp = truncate_text(item[1], col_widths[1], self.font_name, body_font_size)
            so_xe = truncate_text(item[2], col_widths[2], self.font_name, body_font_size)
            don_vi = truncate_text(item[4], col_widths[3], self.font_name, body_font_size)
            so_luong = truncate_text(str(item[5]), col_widths[4], self.font_name, body_font_size)
            don_gia = truncate_text(f"{int(float(item[8])):,}".replace(",", ".") if item[8] else "0", col_widths[5], self.font_name, body_font_size)
            phi_vc = truncate_text(f"{int(float(item[9])):,}".replace(",", ".") if item[9] else "0", col_widths[6], self.font_name, body_font_size)
            thanh_tien = truncate_text(f"{int(float(item[6])):,}".replace(",", "."), col_widths[7], self.font_name, body_font_size)
            noi_giao = truncate_text(item[7], col_widths[8], self.font_name, body_font_size)

            table_data.append([ngay_mua, ten_sp, so_xe, don_vi, so_luong, don_gia, phi_vc, thanh_tien, noi_giao])

        # --- Vẽ các trang ---
        item_index = 0
        page_num = 1

        while item_index < len(items):
            if page_num > 1:
                c.showPage() # Bắt đầu trang mới

            # Vẽ header cho trang đầu tiên
            if page_num == 1:
                self._draw_header(c, invoice_data)
                # THAY ĐỔI: Tăng chiều cao của header để có đủ không gian cho thông tin khách hàng
                header_height = 72 * mm
                footer_height = 30 * mm
                y_start = self.height - self.margin - header_height
                available_height = y_start - self.margin - footer_height
            else:
                # Header đơn giản cho các trang tiếp theo
                c.setFont(self.font_name, 9)
                c.drawString(self.margin, self.height - self.margin, f"Bảng kê khối lượng (tiếp theo) - Trang {page_num}")
                header_height = 15 * mm
                footer_height = 30 * mm
                y_start = self.height - self.margin - header_height
                available_height = y_start - self.margin - footer_height

            # THAY ĐỔI: Chỉ thêm header cho trang đầu tiên
            rows_for_this_page = [table_data[0]] if page_num == 1 else []

            last_fit_index = item_index

            for i in range(item_index, len(items)):
                # Thử thêm dòng tiếp theo
                temp_rows = rows_for_this_page + [table_data[i + 1]] # Luôn dùng dòng đầy đủ để tính toán
                temp_table = Table(temp_rows, colWidths=col_widths)
                temp_table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey)])) # Style đơn giản để tính toán
                
                # Nếu bảng tạm thời vẫn vừa, tiếp tục
                if temp_table.wrapOn(c, self.width, self.height)[1] < available_height:
                    rows_for_this_page.append(table_data[i + 1])
                    last_fit_index = i + 1
                else:
                    break # Dừng lại khi bảng quá lớn

            # Tạo bảng
            table = Table(rows_for_this_page, colWidths=col_widths)
            
            # THAY ĐỔI: Áp dụng style linh hoạt tùy theo trang
            style_commands = [
                # Căn giữa tất cả các ô theo cả chiều ngang và dọc
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]
            if page_num == 1:
                # Style cho trang đầu (có header)
                style_commands.extend([
                    ('FONTNAME', (0, 0), (-1, 0), self.font_name_bold),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12), # Padding cho tiêu đề
                    ('FONTNAME', (0, 1), (-1, -1), self.font_name), # Font cho nội dung
                    ('FONTSIZE', (0, 1), (-1, -1), body_font_size), # Cỡ chữ cho nội dung
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ])
            else:
                # Style cho các trang sau (không có header)
                style_commands.extend([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_name), # Đặt kiểu font cho nội dung
                    ('FONTSIZE', (0, 0), (-1, -1), body_font_size), # Đặt cỡ chữ cho nội dung
                    # THÊM: Đặt padding trên và dưới bằng nhau để căn giữa dọc được cân đối
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ])
            
            style = TableStyle(style_commands)
            table.setStyle(style)

            # Tính toán vị trí và vẽ bảng
            table_width, table_height = table.wrapOn(c, self.width, self.height)
            table_y_pos = y_start - table_height
            table.drawOn(c, self.margin, table_y_pos)
            
            # Vẽ footer nếu đây là trang cuối cùng
            if last_fit_index == len(items):
                self._draw_footer(c, invoice_data, table_y_pos)

            # Cập nhật chỉ số
            item_index = last_fit_index
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

    def export_invoice_pdf(self, invoice_data, items):
        """
        Chỉ tạo file PDF và trả về đường dẫn mà không in.
        """
        if not items:
            return False, "Không có mặt hàng nào để xuất file."
        
        try:
            pdf_path = self.create_invoice_pdf(invoice_data, items)
            return True, f"Đã xuất thành công file PDF tại:\n{pdf_path}"
        except Exception as e:
            logging.error(f"Lỗi trong quá trình xuất PDF: {e}", exc_info=True)
            return False, f"Lỗi khi xuất PDF: {e}"
