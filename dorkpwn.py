#!/usr/bin/env python3
import subprocess
import argparse
import logging
import random
import time
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Setup logging
logging.basicConfig(
    filename="dorking.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"

# ASCII Banner
def print_banner():
    banner = """
     __         __                  
 ___/ /__  ____/ /__ ___ _    _____ 
/ _  / _ \\/ __/  '_// _ \\ |/|/ / _ \\
\\_,_/\\___/_/ /_/\\_\\/ .__/__,__/_//_/
                  /_/      by ~/.manojxshrestha   
    """
    print(f"{RED}{banner}{RESET}")

def setup_session(proxy=None):
    session = requests.Session()
    ua = UserAgent()
    session.headers.update({"User-Agent": ua.random})

    # Setup retries
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Setup proxy if provided
    if proxy:
        session.proxies = {"http": proxy, "https": proxy}
        logging.info(f"Using proxy: {proxy}")

    return session

def read_dorks(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        logging.error(f"Dorks file {file_path} not found")
        print(f"{RED}[ERROR] Dorks file {file_path} not found{RESET}")
        raise

def url_encode(query):
    from urllib.parse import quote
    return quote(query, safe="")

def search_duckduckgo(query, session, retries, delay):
    url = "https://html.duckduckgo.com/html/"
    encoded_query = url_encode(query)
    data = {"q": encoded_query}

    for attempt in range(retries):
        try:
            response = session.post(url, data=data, timeout=15)
            if response.status_code == 429:
                logging.warning(f"Rate limit hit for {query}. Waiting {delay * (attempt + 1)}s")
                print(f"{RED}[WARNING] Rate limit hit for {query}. Waiting {delay * (attempt + 1)}s{RESET}")
                time.sleep(delay * (attempt + 1))
                continue
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            links = [
                link.get("href") for link in soup.select(".result__url")
                if link.get("href") and not any(x in link.get("href") for x in ["duckduckgo.com", "about:"])
            ]
            logging.info(f"Fetched {len(links)} results for query: {query}")
            return links
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt + 1}/{retries} failed for {query}: {e}")
            print(f"{RED}[WARNING] Attempt {attempt + 1}/{retries} failed for {query}: {e}{RESET}")
            time.sleep(delay * (attempt + 1))
    logging.error(f"Failed to fetch {query} after {retries} attempts")
    print(f"{RED}[ERROR] Failed to fetch {query} after {retries} attempts{RESET}")
    return []

def filter_live_urls(urls, temp_file="temp_urls.txt"):
    try:
        # Write URLs to a temp file for httpx
        with open(temp_file, "w", encoding="utf-8") as f:
            for url in urls:
                f.write(f"{url}\n")

        # Run httpx to filter live URLs
        httpx_cmd = [
            "httpx",
            "-l", temp_file,
            "-silent",
            "-mc", "200,301,302,403,401",
            "-timeout", "10"
        ]
        result = subprocess.run(httpx_cmd, capture_output=True, text=True)

        # Parse httpx output
        live_urls = result.stdout.strip().split("\n") if result.stdout.strip() else []
        logging.info(f"Filtered {len(live_urls)} live URLs with httpx")
        print(f"{GREEN}[INFO] Filtered {len(live_urls)} live URLs{RESET}")

        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)

        return live_urls
    except subprocess.CalledProcessError as e:
        logging.error(f"httpx failed: {e}")
        print(f"{RED}[ERROR] httpx failed: {e}{RESET}")
        return []
    except Exception as e:
        logging.error(f"Error filtering URLs: {e}")
        print(f"{RED}[ERROR] Error filtering URLs: {e}{RESET}")
        return []

def main():
    # Print banner
    print_banner()
    
    # Interactive input
    print(f"{GREEN}[+] Enter The Target site: {RESET}", end="")
    target = input().strip()

    print(f"{GREEN}[+] Enter The Dorks file (e.g., dorks.txt): {RESET}", end="")
    dorks_file = input().strip()

    print(f"{GREEN}[+] Enter Total Number of Results You Want (or type 'all' to fetch everything): {RESET}", end="")
    user_choice = input().strip().lower()
    if user_choice == "all":
        total_results = float("inf")
    else:
        try:
            total_results = int(user_choice)
            if total_results <= 0:
                raise ValueError
        except ValueError:
            logging.error("Invalid number of results entered")
            print(f"{RED}[ERROR] Please enter a positive integer or 'all'{RESET}")
            return

    print(f"{GREEN}[+] Do You Want to Save the Output? (Y/N): {RESET}", end="")
    save_output = input().strip().lower()
    output_file = "results.txt"
    if save_output == "y":
        print(f"{GREEN}[+] Enter Output Filename (e.g., results.txt): {RESET}", end="")
        output_file_input = input().strip()
        if output_file_input:
            output_file = output_file_input if output_file_input.endswith(".txt") else f"{output_file_input}.txt"

    # Setup proxy (optional)
    proxy = None
    print(f"{GREEN}[+] Enter Proxy URL (e.g., http://proxy:port, leave empty for none): {RESET}", end="")
    proxy_input = input().strip()
    if proxy_input:
        proxy = proxy_input

    # Setup session
    session = setup_session(proxy)

    # Read dorks
    try:
        dorks = read_dorks(dorks_file)
        logging.info(f"Loaded {len(dorks)} dorks from {dorks_file}")
        print(f"{GREEN}[INFO] Loaded {len(dorks)} dorks{RESET}")
    except Exception:
        return

    print(f"\n{GREEN}[INFO] Searching... Please wait...{RESET}\n")

    all_results = []
    retries = 3
    delay = 10.0
    fetched = 0

    for dork in dorks:
        if fetched >= total_results:
            break

        query = f"site:{target} {dork}" if target else dork
        print(f"{GREEN}[+] Searching: {query}{RESET}")
        logging.info(f"Processing query: {query}")

        # Perform search
        links = search_duckduckgo(query, session, retries, delay)

        # Filter live URLs with httpx
        if links:
            live_links = filter_live_urls(links)
            if live_links:
                all_results.extend(live_links)
                fetched += len(live_links)
                for link in live_links:
                    print(f"{GREEN}[+] {link}{RESET}")
            else:
                print(f"{RED}[-] No live URLs for {query}{RESET}")
        else:
            print(f"{RED}[-] No results for {query}{RESET}")

        # Add a one-line gap after each dork
        print()

        # Random delay
        sleep_time = random.uniform(delay, delay + 5)
        logging.info(f"Sleeping for {sleep_time:.2f}s")
        time.sleep(sleep_time)

    # Save results
    if save_output == "y" and all_results:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for link in all_results:
                    f.write(f"{link}\n")
            print(f"\n{GREEN}[✓] Saved {len(all_results)} live URLs to {output_file}{RESET}")
            logging.info(f"Saved {len(all_results)} live URLs to {output_file}")
        except Exception as e:
            logging.error(f"Failed to save results: {e}")
            print(f"{RED}[ERROR] Failed to save results: {e}{RESET}")

    print(f"\n{GREEN}[✓] Automation Done{RESET}")
    logging.info("Dorking completed")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}[!] User Interruption Detected! Exiting...{RESET}")
        logging.info("Script interrupted by user")
        exit(1)
