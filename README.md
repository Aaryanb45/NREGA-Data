# NREGA-Data
This project automates the extraction of **Company Master Data** from the [MCA (Ministry of Corporate Affairs)](https://www.mca.gov.in/) portal using:

- **Selenium + Selenium Wire** for web automation & proxy support  
-  **OpenCV + Tesseract OCR** for automated CAPTCHA solving  
- **Windscribe VPN** for secure and region-consistent scraping  
-  **Excel Export Automation** for saving data into structured `.xlsx` files  

---

##  Features
- Automatically connects to **Windscribe VPN** before scraping
- Navigates to **MCA Master Data Search (MDS)** page
- Handles **CAPTCHA solving** (basic + enhanced OCR modes)
- Clicks **CIN links** and extracts full company data
- Exports data via MCA’s **"Export All Tabs (Excel)"** button
- Renames Excel files to:  

company_master_data.xlsx

##  Tech Stack
- **Language**: Python 3.10+
- **Automation**: [Selenium](https://www.selenium.dev/) + [Selenium Wire](https://pypi.org/project/selenium-wire/)
- **OCR**: [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) + [OpenCV](https://opencv.org/)
- **VPN Handling**: Windscribe CLI (`windscribe-cli`)
- **Data Handling**: Pandas
- **Browser Driver**: ChromeDriver (auto-managed via `webdriver_manager`)

---

## 📂 Project Structure
.
├── app.py # Main script
├── requirements.txt # Python dependencies
├── /company_master_data # Downloaded Excel files
├── /captchas # Saved CAPTCHA screenshots
└── CIN of Firms in ProwessDx.xlsx # Input CIN list


---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/mca-scraper.git
cd mca-scraper

python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows

Install dependencies
pip install -r requirements.txt



nstall Tesseract OCR

macOS: brew install tesseract

Ubuntu: sudo apt install tesseract-ocr

Windows: Download installer

 Install Windscribe CLI

Windscribe CLI Download

 Update your credentials

Edit in app.py:

WINDSCRIBE_USERNAME = "your_username"
WINDSCRIBE_PASSWORD = "your_password"

 Usage

Place your CIN list in CIN of Firms in ProwessDx.xlsx

Make sure there’s a column named CIN or CIN of Firms

Run the scraper:

python app.py


Output will be saved in:

/company_master_data/<CIN>_company_master_data.xlsx

 Notes

MCA portal uses strict anti-bot measures.
This script includes:

Random delays

VPN rotation

OCR-based CAPTCHA solving

Even then, 100% success is not guaranteed.
If CAPTCHA fails → script retries automatically.

 Disclaimer

This project is for educational & research purposes only.
Scraping government portals may violate their Terms of Use.
Please use responsibly and ensure compliance with applicable laws.

 Author

Aryan Bansal
aryanbansal182004@gmail.com


