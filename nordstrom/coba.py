import undetected_chromedriver as uc
import time

driver = uc.Chrome()
driver.get("https://www.nordstrom.com/")
time.sleep(5)

driver.get("https://www.nordstrom.com/browse/beauty")
time.sleep(100)

print("Opened!")
