
# 🛒 Amazon Price Tracker

A simple desktop app to track Amazon product prices and get notified by email (and Windows notifications) when your target price is reached. Supports both single product and bulk tracking via `.txt` file.

---

## ✨ Features

- **Track Single Product:** Enter a product URL and target price to monitor.
- **Bulk Tracking:** Upload a `.txt` file with multiple products and target prices.
- **Email Alerts:** Get notified when a product drops below your target price.
- **Windows Notifications:** Optional toast notifications on Windows.
- **Auto Price Check:** Enable periodic automatic checks with a countdown timer.
- **User-Friendly GUI:** Built with PyQt5 for a clean and simple interface.

---

## 📦 Requirements

- Python 3.7+
- [PyQt5](https://pypi.org/project/PyQt5/)
- [requests](https://pypi.org/project/requests/)
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
- [lxml](https://pypi.org/project/lxml/)
- (Optional, Windows only) [win10toast](https://pypi.org/project/win10toast/)

Install dependencies:
```bash
pip install PyQt5 requests beautifulsoup4 lxml
# For Windows notifications:
pip install win10toast
```

---

## 🚀 Usage

1. **Run the App:**
    ```bash
    python price_tracker.py
    ```

2. **Track a Single Product:**
    - Paste the Amazon product URL.
    - Enter your target price (₹).
    - Enter your Gmail address and [App Password](https://support.google.com/accounts/answer/185833).
    - (Optional) Set auto-check interval (minutes).
    - Click **"Track Single Product"**.

3. **Bulk Tracking:**
    - Prepare a `.txt` file with each line as:
      ```
      <amazon_url>,<target_price>
      ```
      Example:
      ```
      https://www.amazon.in/dp/B09G9FPGTN,49999
      https://www.amazon.in/dp/B07DJCVTBH,2999
      ```
    - Click **"Upload .txt File for Bulk Tracking"** and select your file.

4. **Enable Auto Price Check:**
    - Check the **"Enable Auto Price Check"** box.
    - The app will check prices at your set interval and show a countdown.

---

## 📧 Email Setup

- Use your Gmail address and an **App Password** (not your regular password).
- [How to generate an App Password](https://support.google.com/accounts/answer/185833).

---

## 🖥️ Windows Notifications

- On Windows, install `win10toast` for desktop notifications.
- Notifications are sent when a price drop is detected.

---

## 📝 Notes

- Only works for Amazon India (₹) product pages.
- The app scrapes product title and price; if Amazon changes their page structure, updates may be needed.
- Your credentials are used only for sending notification emails.

---

## 🛠️ Troubleshooting

- **Email not sending?**  
  - Ensure you use an App Password, not your Gmail password.
  - Check your internet connection.
- **No price detected?**  
  - Make sure the product URL is correct and public.
  - Amazon may block requests if too frequent.

---

## 📄 License

MIT License

---

## 🙏 Credits

- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [win10toast](https://github.com/jithurjacob/Windows-10-Toast-Notifications)

---
