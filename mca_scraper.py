
import pandas as pd
from selenium import webdriver
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re

def solve_captcha_ocr(captcha_image_path):
    try:
        img = cv2.imread(captcha_image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        pil_img = Image.fromarray(cleaned)
        enhancer = ImageEnhance.Contrast(pil_img)
        enhanced = enhancer.enhance(2.0)
        filtered = enhanced.filter(ImageFilter.MedianFilter())
        custom_config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        captcha_text = pytesseract.image_to_string(filtered, config=custom_config).strip()
        captcha_text = clean_captcha_text(captcha_text)
        return captcha_text
    except Exception as e:
        print(f"OCR Error: {e}")
        return None

def solve_captcha_advanced_ocr(captcha_image_path):
    try:
        original = cv2.imread(captcha_image_path)
        approaches = []
        gray1 = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        _, thresh1 = cv2.threshold(gray1, 127, 255, cv2.THRESH_BINARY)
        approaches.append(thresh1)
        gray2 = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        adaptive = cv2.adaptiveThreshold(gray2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        approaches.append(adaptive)
        gray3 = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        kernel = np.ones((2, 2), np.uint8)
        eroded = cv2.erode(gray3, kernel, iterations=1)
        dilated = cv2.dilate(eroded, kernel, iterations=1)
        approaches.append(dilated)
        gray4 = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray4, 50, 150)
        edges_inv = cv2.bitwise_not(edges)
        approaches.append(edges_inv)
        results = []
        for i, img in enumerate(approaches):
            try:
                psm_modes = [8, 7, 13, 6]
                for psm in psm_modes:
                    config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                    text = pytesseract.image_to_string(img, config=config).strip()
                    cleaned_text = clean_captcha_text(text)
                    if cleaned_text and len(cleaned_text) == 6:
                        results.append(cleaned_text)
            except:
                continue
        if results:
            return max(set(results), key=results.count) if len(set(results)) > 1 else results[0]
        return None
    except Exception as e:
        print(f"Advanced OCR Error: {e}")
        return None

def solve_captcha_enhanced_ocr(captcha_image_path):
    try:
        img = cv2.imread(captcha_image_path)
        height, width = img.shape[:2]
        img = cv2.resize(img, (width * 3, height * 3), interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        results = []
        _, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        _, thresh3 = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        _, thresh4 = cv2.threshold(gray, 140, 255, cv2.THRESH_BINARY)
        kernel = np.ones((2, 2), np.uint8)
        thresh1_clean = cv2.morphologyEx(thresh1, cv2.MORPH_CLOSE, kernel)
        thresh2_clean = cv2.morphologyEx(thresh2, cv2.MORPH_CLOSE, kernel)
        processed_images = [thresh1, thresh2, thresh3, thresh4, thresh1_clean, thresh2_clean]
        for i, processed_img in enumerate(processed_images):
            try:
                for psm in [8, 7, 13, 6]:
                    config = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                    text = pytesseract.image_to_string(processed_img, config=config).strip()
                    cleaned = clean_captcha_text(text)
                    if cleaned and len(cleaned) >= 4:
                        results.append(cleaned)
                        print(f"Method {i+1}, PSM {psm}: {cleaned}")
            except:
                continue
        if results:
            from collections import Counter
            counter = Counter(results)
            most_common = counter.most_common(1)[0][0]
            print(f"Most common result: {most_common}")
            return most_common
        return None
    except Exception as e:
        print(f"Enhanced OCR Error: {e}")
        return None

def clean_captcha_text(text):
    if not text:
        return None
    cleaned = re.sub(r'[^A-Za-z0-9]', '', text)
    if len(cleaned) >= 6:
        return cleaned[:6]
    elif len(cleaned) >= 4:
        return cleaned
    else:
        return None

def wait_for_captcha(driver, timeout=30):
    WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "img[alt='captcha']")))

def solve_and_submit_captcha(driver, captcha_file_path):
    captcha_text = None
    print("Trying enhanced OCR...")
    captcha_text = solve_captcha_enhanced_ocr(captcha_file_path)
    if captcha_text and len(captcha_text) == 6:
        print(f"Enhanced OCR solved captcha: {captcha_text}")
    else:
        captcha_text = None
    if not captcha_text:
        print("Trying advanced OCR...")
        captcha_text = solve_captcha_advanced_ocr(captcha_file_path)
        if captcha_text:
            print(f"Advanced OCR solved captcha: {captcha_text}")
    if not captcha_text:
        print("Trying basic OCR...")
        captcha_text = solve_captcha_ocr(captcha_file_path)
        if captcha_text:
            print(f"Basic OCR solved captcha: {captcha_text}")
    if not captcha_text:
        print("Automatic captcha solving failed. Moving to next main attempt.")
        return False
    if captcha_text and len(captcha_text) != 6:
        print(f"Warning: Captcha text '{captcha_text}' is not 6 characters. Truncating/padding.")
        captcha_text = captcha_text[:6] if len(captcha_text) > 6 else captcha_text
    print(f"Final captcha text to submit: '{captcha_text}'")
    captcha_input = driver.find_element(By.ID, "customCaptchaInput")
    captcha_input.clear()
    captcha_input.send_keys(captcha_text)
    submit_btn = driver.find_element(By.ID, "check")
    driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
    time.sleep(0.5)
    submit_btn.click()
    time.sleep(3)
    try:
        error_element = driver.find_element(By.XPATH, "//*[contains(text(), 'incorrect') or contains(text(), 'retry')]")
        if error_element:
            print("Captcha was incorrect.")
            return False
    except:
        return True
    return True

def handle_second_captcha(driver, cin, file_path):
    try:
        print("Waiting for second captcha to appear...")
        wait_for_captcha(driver, timeout=15)
        captcha_img2 = driver.find_element(By.CSS_SELECTOR, "img[alt='captcha']")
        captcha_file2 = os.path.join(file_path, f"captcha_{cin}_step2.png")
        with open(captcha_file2, 'wb') as f:
            f.write(captcha_img2.screenshot_as_png)
        print(f"[INFO] Second captcha image saved at {captcha_file2}.")
        return solve_and_submit_captcha(driver, captcha_file2)
    except Exception as e:
        print("[WARN] No second captcha appeared. Maybe already on details page or an error occurred.")
        print("Error:", e)
        return False

def click_cin_link(driver, cin):
    try:
        u_cin = driver.find_element(By.XPATH, f"//u[contains(@class, 'company-id') and normalize-space(text())='{cin}']")
        print("[INFO] Found CIN <u> element. Trying JS click...")
        driver.execute_script("arguments[0].scrollIntoView(true);", u_cin)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", u_cin)
        print("[INFO] JS click on CIN <u> element successful.")
        return True
    except Exception as e:
        print(f"[-] Could not click CIN <u> element: {e}")

    try:
        js = f'''
        var el = Array.from(document.querySelectorAll('u.company-id')).find(e => e.textContent.trim() === '{cin}');
        if(el) {{
            el.scrollIntoView();
            el.click();
            return true;
        }} else {{
            return false;
        }}
        '''
        found = driver.execute_script(js)
        if found:
            print("[INFO] JS DOM search and click on CIN <u> element successful.")
            return True
        else:
            print("[-] JS DOM search failed to find CIN <u> element.")
    except Exception as e:
        print(f"[-] JS DOM search/click error: {e}")

    print("[-] CIN <u> element not found/clickable by any method.")
    return False

def export_all_tabs_excel(driver):
    try:
        export_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Export')]"))
        )
        export_btn.click()
        time.sleep(1)
        export_all_excel = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Export All Tabs(Excel)')]"))
        )
        export_all_excel.click()
        print("[INFO] Clicked Export All Tabs(Excel). Waiting for download to complete...")
        time.sleep(10)
        return True
    except Exception as e:
        print(f"[ERROR] Export All Tabs(Excel) failed: {e}")
        return False

def scrape_with_auto_captcha(cin, file_path, save_folder):
    from selenium.webdriver.firefox.options import Options

    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", save_folder)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    options.set_preference("pdfjs.disabled", True)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)
    try:
        driver.get("https://mca.gov.in/content/mca/global/en/mca/master-data/MDS.html")
        time.sleep(3)
        search_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder*='CIN']")
        search_input.clear()
        search_input.send_keys(cin)
        search_input.send_keys(Keys.RETURN)
        time.sleep(2)
        wait_for_captcha(driver)
        captcha_img = driver.find_element(By.CSS_SELECTOR, "img[alt='captcha']")
        captcha_file_path = os.path.join(file_path, f"captcha_{cin}.png")
        with open(captcha_file_path, 'wb') as f:
            f.write(captcha_img.screenshot_as_png)
        print(f"First captcha image saved at {captcha_file_path}")

        if not solve_and_submit_captcha(driver, captcha_file_path):
            return False

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, "//table")))
        tables = driver.find_elements(By.TAG_NAME, "table")
        target_table = None
        for tbl in tables:
            headers = [th.text.strip() for th in tbl.find_elements(By.TAG_NAME, "th")]
            if "Company/LLP name" in headers or "CIN/FCRN/LLPIN/FLLPIN" in headers:
                target_table = tbl
                break
        if not target_table:
            print("Could not find results table.")
            return False
        rows = target_table.find_elements(By.TAG_NAME, "tr")
        data = []
        for i, row in enumerate(rows):
            cols = row.find_elements(By.TAG_NAME, "th") + row.find_elements(By.TAG_NAME, "td")
            col_texts = [col.text.strip() for col in cols]
            if col_texts:
                data.append(col_texts)
        if len(data) > 1:
            header = data[0]
            fixed_data = []
            for row in data[1:]:
                if len(row) < len(header):
                    row = row + [""] * (len(header) - len(row))
                elif len(row) > len(header):
                    row = row[:len(header)]
                fixed_data.append(row)
            df = pd.DataFrame(fixed_data, columns=header)
            df.to_csv(os.path.join(save_folder, f"{cin}_basic.csv"), index=False)
            print(f"Saved basic data for {cin}:")
            print(df)
        print("\n--- Starting Step 2: Clicking CIN for detailed company information ---")
        driver.save_screenshot(os.path.join(file_path, f"debug_before_click_{cin}.png"))
        with open(os.path.join(file_path, f"mca_debug_page_{cin}.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("[DEBUG] Wrote the full HTML to mca_debug_page.html")
        if not click_cin_link(driver, cin):
            print("[FATAL] Could not click CIN <u> element. Check output and try again.")
            return False
        time.sleep(2)
        if not handle_second_captcha(driver, cin, file_path):
            print("[FATAL] Could not solve second captcha, try again.")
            return False

        time.sleep(3)
        with open(os.path.join(file_path, f"mca_company_detail_page_after_captcha2_{cin}.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("[DEBUG] Wrote company detail HTML after captcha 2 to mca_company_detail_page_after_captcha2.html")
        if not export_all_tabs_excel(driver):
            print("[FATAL] Could not export all tabs as Excel.")
            return False

        print(f"[SUCCESS] Exported all tabs Excel for CIN {cin}.")
        return True
    except Exception as e:
        print(f"Error for {cin}: {e}")
        return False
    finally:
        driver.quit()

def scrape_multiple_cins(cin_list, file_path, save_folder):
    for cin in cin_list:
        print(f"\n====== Starting CIN: {cin} ======")
        attempt = 1
        while True:
            print(f"\n=== Attempt {attempt} for CIN {cin} ===")
            success = scrape_with_auto_captcha(cin, file_path, save_folder)
            if success:
                print(f"\n✅ Scraping completed successfully for {cin}!")
                break
            else:
                print(f"❌ Attempt {attempt} failed for {cin}. Restarting for same CIN in 10 seconds ...")
                time.sleep(10)
            attempt += 1

if __name__ == "__main__":
    # List of CINs (add/remove as needed)
    cin_list = [
        "U63090MH1971PTC015089",
        "L99999GJ1987PLC009768",
        "U31900DL1984PLC018942",
        "U65990MH1978PTC020803",
        "U99999MH1979PTC021609",
        "U92110MH1944PTC004242",
        "U36911RJ1984PLC003144",
        "U67120MH1980PTC022516",
        "U52100MH1991PTC062058",
        "U27106WB1985PLC039264"
    ]

    file_path = r"/Users/aryanbansal/Desktop/IIM_BANGLORE_INTERNSHIP"
    save_folder = r"/Users/aryanbansal/Desktop/IIM_BANGLORE_INTERNSHIP/company_master_data"
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    scrape_multiple_cins(cin_list, file_path, save_folder)