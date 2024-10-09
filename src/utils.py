from selenium_driverless import webdriver
import asyncio
import time
import csv
import os


async def start_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # uncomment this line to run in headless mode
    # options.add_argument("--disable-gpu")  # comment to run in a cloud
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--detach")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-translate")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--disable-features=IsolateOrigins,site-per-process")
    options.add_argument("--disable-features=BlockInsecurePrivateNetworkRequests")
    options.add_argument("--disable-features=OutOfBlinkCors")
    options.add_argument("--disable-features=SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    options.add_argument("--disable-features=CrossSiteDocumentBlockingIfIsolating,CrossSiteDocumentBlockingAlways")
    options.add_argument("--disable-features=ImprovedCookieControls,LaxSameSiteCookies,SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure")
    options.add_argument("--disable-features=SameSiteDefaultChecksMethodRigorously")
    driver = await webdriver.Chrome(options=options)
    return driver


async def wait_for_selector(driver, by, selector, timeout=30, check_interval=0.5, response=None, visible=False):
    start_time = asyncio.get_event_loop().time()
    while (asyncio.get_event_loop().time() - start_time) < timeout:
        try:
            element = await driver.find_element(by, selector, timeout=check_interval)

            if not visible and element:
                return response or element

            if element:
                is_visible = await element.is_displayed()
                if is_visible:
                    return response or element
        except Exception:
            pass

        await asyncio.sleep(check_interval)


async def race(*coroutines):
    done, pending = await asyncio.wait(coroutines, return_when=asyncio.FIRST_COMPLETED)
    for task in pending:
        task.cancel()
    return done.pop().result()


async def wait_for_network_idle(driver, max_connections=0, timeout=30, idle_time=0.5):
    start_time = time.time()
    while time.time() - start_time < timeout:
        active_requests = await driver.execute_script("""
            var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {};
            var entries = performance.getEntriesByType && performance.getEntriesByType('resource') || [];
            return entries.filter(function(entry) {
                return !entry.responseEnd;
            }).length;
        """)

        if active_requests <= max_connections:
            time.sleep(idle_time)

            active_requests = await driver.execute_script("""
                var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {};
                var entries = performance.getEntriesByType && performance.getEntriesByType('resource') || [];
                return entries.filter(function(entry) {
                    return !entry.responseEnd;
                }).length;
            """)

            if active_requests <= max_connections:
                time.sleep(2)
                return True

        time.sleep(0.1)

    return False


def save_success_csv(data, file_path):
    def clean_for_csv(text):
        if isinstance(text, str):
            return text.replace("\n", " ").replace("\r", "").replace('"', '""')
        return text

    if not isinstance(data, list):
        data = [data]

    creator_data_path_exists = os.path.exists(file_path)
    creator_data_file_empty = creator_data_path_exists and os.path.getsize(file_path) == 0

    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys(), quoting=csv.QUOTE_ALL)
        if not creator_data_path_exists or creator_data_file_empty:
            writer.writeheader()
        cleaned_users = [{k: clean_for_csv(v) for k, v in user.items()} for user in data]
        writer.writerows(cleaned_users)


def save_errors(file_path, *args):
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([*args])
