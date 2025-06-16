import smtplib, os
from email.message import EmailMessage
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_register_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Xác thực đăng ký tài khoản"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(
        f"""
        Xin chào,
        Đây là mã OTP để xác thực đăng ký tài khoản của bạn: {otp}
        Mã này sẽ hết hạn sau 5 phút.

        Trân trọng,
        Đội ngũ hỗ trợ
        """
    )
    try:
        print("🚀 Đang gửi email...")
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()  # Bắt đầu TLS
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print(f"✅ Gửi OTP {otp} đến {to_email} thành công.")
    except Exception as e:
        print("❌ Lỗi khi gửi email:", e)
        
def send_forgot_password_otp_email(to_email: str, otp: str):
    body = f"""
    Xin chào,
    Mã OTP để đặt lại mật khẩu của bạn là: {otp}
    Mã này sẽ hết hạn sau 5 phút.
    Trân trọng,
    Đội ngũ hỗ trợ
    """
    msg = MIMEText(body)
    msg["Subject"] = "Quên mật khẩu - Mã OTP xác thực"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)