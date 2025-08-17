import sys
import platform
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFormLayout, QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer

if platform.system() == "Windows":
    try:
        from win10toast import ToastNotifier
    except ImportError:
        ToastNotifier = None
else:
    ToastNotifier = None


class PriceTrackerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Amazon Price Tracker 🛒")
        self.setGeometry(100, 100, 600, 600)

        self.timer = QTimer()
        self.countdown_timer = QTimer()
        self.remaining_seconds = 0
        self.txt_file_path = None

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.url_input = QLineEdit()
        self.target_price_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.interval_input = QLineEdit()
        self.interval_input.setPlaceholderText("e.g. 60 (minutes)")

        form_layout.addRow("🔗 Product URL:", self.url_input)
        form_layout.addRow("💰 Target Price (₹):", self.target_price_input)
        form_layout.addRow("📧 Your Email:", self.email_input)
        form_layout.addRow("🔒 App Password:", self.password_input)
        form_layout.addRow("⏰ Auto Check Interval (minutes):", self.interval_input)

        layout.addLayout(form_layout)

        self.track_button = QPushButton("Track Single Product")
        self.track_button.clicked.connect(self.track_single_product)
        layout.addWidget(self.track_button)

        self.upload_button = QPushButton("📤 Upload .txt File for Bulk Tracking")
        self.upload_button.clicked.connect(self.upload_txt_file)
        layout.addWidget(self.upload_button)

        self.auto_check_box = QCheckBox("🔁 Enable Auto Price Check")
        self.auto_check_box.stateChanged.connect(self.toggle_auto_check)
        layout.addWidget(self.auto_check_box)

        self.countdown_label = QLabel("⏳ Next check: -- minutes")
        layout.addWidget(self.countdown_label)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(QLabel("📄 Output:"))
        layout.addWidget(self.output)

        self.setLayout(layout)

    def show_message(self, msg):
        self.output.append(msg)

    def send_email(self, subject, message, user_email, app_password):
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = user_email
            msg["To"] = user_email
            msg.set_content(message)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(user_email, app_password)
                smtp.send_message(msg)
                self.show_message("✅ Email sent!")
        except Exception as e:
            self.show_message(f"❌ Email Error: {e}")

    def notify_windows(self, title, message):
        if ToastNotifier:
            try:
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=10)
                self.show_message("🖥️ Windows notification sent.")
            except Exception as e:
                self.show_message(f"⚠️ Notification error: {e}")

    def track_single_product(self):
        url = self.url_input.text().strip()
        try:
            target_price = int(self.target_price_input.text().strip())
        except ValueError:
            self.show_message("⚠️ Invalid target price.")
            return

        user_email = self.email_input.text().strip()
        app_password = self.password_input.text().strip()

        if not all([url, user_email, app_password]):
            self.show_message("⚠️ Fill all fields.")
            return

        self.track_product(url, target_price, user_email, app_password)

    def upload_txt_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select .txt File", "", "Text Files (*.txt)")
        if not file_path:
            return

        self.txt_file_path = file_path

        user_email = self.email_input.text().strip()
        app_password = self.password_input.text().strip()

        if not user_email or not app_password:
            self.show_message("⚠️ Enter email and app password first.")
            return

        self.track_all_from_txt()

    def track_all_from_txt(self):
        if not self.txt_file_path:
            self.show_message("⚠️ No .txt file uploaded.")
            return

        user_email = self.email_input.text().strip()
        app_password = self.password_input.text().strip()

        try:
            with open(self.txt_file_path, "r") as f:
                for line in f:
                    if "," in line:
                        url, price_str = line.strip().split(",", 1)
                        try:
                            target_price = int(price_str)
                            self.track_product(url.strip(), target_price, user_email, app_password)
                        except ValueError:
                            self.show_message(f"⚠️ Invalid price in line: {line.strip()}")
        except Exception as e:
            self.show_message(f"❌ Error reading file: {e}")

    def track_product(self, url, target_price, user_email, app_password):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9"
        }

        try:
            res = requests.get(url, headers=headers)
            soup = BeautifulSoup(res.content, "lxml")

            title_tag = soup.find(id="productTitle")
            price_tag = soup.find("span", class_="a-price-whole")

            if not title_tag or not price_tag:
                self.show_message("❌ Could not extract product info.")
                return

            title = title_tag.get_text(strip=True)
            price_text = price_tag.get_text(strip=True)
            price = int(price_text.replace(",", "").replace(".", ""))

            self.show_message(f"🛍️ {title}\n💵 ₹{price}")

            if price <= target_price:
                subject = "🔔 Price Drop Alert!"
                message = f"{title}\nCurrent Price: ₹{price}\nLink: {url}"
                self.send_email(subject, message, user_email, app_password)

                if platform.system() == "Windows":
                    self.notify_windows(subject, message)
            else:
                self.show_message("ℹ️ Price above target.")

        except Exception as e:
            self.show_message(f"❌ Error checking product: {e}")

    def toggle_auto_check(self):
        self.timer.stop()
        self.countdown_timer.stop()
        self.timer.timeout.disconnect()
        self.countdown_timer.timeout.disconnect()

        if self.auto_check_box.isChecked():
            try:
                interval_min = int(self.interval_input.text().strip())
            except ValueError:
                self.show_message("⚠️ Invalid interval.")
                self.auto_check_box.setChecked(False)
                return

            interval_ms = interval_min * 60 * 1000
            self.remaining_seconds = interval_min * 60

            # Which method to auto-track
            if self.txt_file_path:
                self.timer.timeout.connect(self.track_all_from_txt)
                self.show_message(f"⏳ Auto-check every {interval_min} min for .txt file")
            else:
                self.timer.timeout.connect(self.track_single_product)
                self.show_message(f"⏳ Auto-check every {interval_min} min for single product")

            self.timer.start(interval_ms)

            # Countdown timer updates UI
            self.countdown_timer.timeout.connect(self.update_countdown)
            self.countdown_timer.start(1000)

            self.update_countdown()

        else:
            self.countdown_label.setText("⏳ Next check: -- minutes")
            self.show_message("🛑 Auto-check disabled.")

    def update_countdown(self):
        if self.remaining_seconds <= 0:
            self.remaining_seconds = int(self.interval_input.text().strip()) * 60
        mins, secs = divmod(self.remaining_seconds, 60)
        self.countdown_label.setText(f"⏳ Next check in: {mins:02d}:{secs:02d}")
        self.remaining_seconds -= 1


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PriceTrackerApp()
    window.show()
    sys.exit(app.exec_())