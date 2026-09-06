import requests
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright

def download_proxy_list():
    try:
        response = requests.get("https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt", timeout=10)
        if response.status_code == 200:
            proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
            return proxies
    except Exception as e:
        print(f"Download error: {e}")
    return []

def check_single_proxy(proxy):
    test_url = "https://httpbin.org/ip"
    proxies_dict = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}"
    }
    
    try:
        response = requests.get(test_url, proxies=proxies_dict, timeout=3)
        if response.status_code == 200:
            print(f"[ACTIVE] {proxy} -> {response.json().get('origin')}")
            return proxy
    except:
        pass
    return None

def check_proxies_batch(proxy_list, max_threads=50):
    working_proxies = []
    print("Checking proxies...")
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(check_single_proxy, proxy_list)
        for result in results:
            if result:
                working_proxies.append(result)
                
    print(f"Done, working proxies: {len(working_proxies)}/{len(proxy_list)}")
    return working_proxies

def run_browser():
    with sync_playwright() as p:
        user_data_dir = "./profiles/test_user"

        proxy_config = {
            "server": "http://127.0.0.1:8080",
            # "username": "login",
            # "password": "password"
        }

        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
            ],
            proxy=proxy_config,
            viewport={"width": 1280, "height": 720},
            locale="ru-RU",
            timezone_id="Europe/Moscow"
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });

            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });

            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US', 'en']
            });
        """)

        page = context.new_page()
        page.goto("https://google.com/")
        
        input("Press Enter for close...")
        context.close()

if __name__ == "__main__":
    # run_browser()
    proxies = download_proxy_list()
    check_proxies_batch(proxies[:500])