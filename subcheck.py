#!/usr/bin/env python3
import requests
import argparse
import pyfiglet
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin
from tqdm import tqdm
import signal
import sys
from collections import defaultdict

# Global variables for stopping and storing results
stop_requested = False
status_count = defaultdict(int)  # Default dictionary untuk menghitung status codes

# Fungsi untuk menangani sinyal Ctrl+C (SIGINT)
def signal_handler(sig, frame):
    global stop_requested
    print("\n\033[91mProses dihentikan.\033[0m")
    stop_requested = True
    sys.exit(0)

# Mendaftarkan handler untuk Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Fungsi untuk menampilkan judul
def print_title():
    title = pyfiglet.figlet_format("Subdomain Validator")
    subtitle = "by zeroMAN555"
    print(f"\033[96m{title}\033[0m")  # Warna Cyan untuk judul
    print(f"\033[93m{subtitle}\033[0m")  # Warna Kuning untuk subtitle
    print("=" * 80)

# Fungsi untuk melakukan permintaan HTTP
def check_subdomain(url, timeout=10):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code
    except requests.RequestException:
        return None

# Fungsi untuk melakukan validasi subdomain
def validate_subdomains(subdomains, base_url, threads=10, timeout=10):
    global status_count
    with tqdm(total=len(subdomains), desc="Progres", unit="sub", ncols=100) as pbar:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(check_subdomain, urljoin(base_url, subdomain), timeout=timeout): subdomain for subdomain in subdomains}

            for future in as_completed(futures):
                status_code = future.result()
                pbar.update(1)

                subdomain = futures[future]
                if status_code == 200:
                    status_count["200"] += 1
                    print(f"\033[92m{subdomain} [Status: {status_code}]\033[0m")  # Hijau untuk 200
                elif status_code == 404:
                    status_count["404"] += 1
                    print(f"\033[93m{subdomain} [Status: {status_code}]\033[0m")  # Kuning untuk 404
                elif status_code is not None:
                    status_count[str(status_code)] += 1  # Hitung status selain 200 dan 404
                    print(f"\033[91m{subdomain} [Status: {status_code}]\033[0m")  # Merah untuk status selain 200/404
                else:
                    print(f"\033[90m{subdomain} [Tidak ada response]\033[0m")  # Abu-abu jika tidak ada response

# Fungsi untuk mencetak hasil akhir
def print_summary():
    print("\n\033[94mSummary:\033[0m")
    for status, count in status_count.items():
        if status == "200":
            print(f"\033[92m200 OK   : {count}\033[0m")
        elif status == "404":
            print(f"\033[93m404 Not Found: {count}\033[0m")
        else:
            print(f"\033[91mStatus {status} : {count}\033[0m")

# Argumen command line
def main():
    print_title()

    parser = argparse.ArgumentParser(description="Check status subdomain.")
    
    parser.add_argument("-u", "--url", required=True, help="Base URL (misal: https://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path ke wordlist yang berisi subdomain")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Jumlah threads yang digunakan (default: 10)")
    parser.add_argument("-timeout", "--timeout", type=int, default=10, help="Timeout untuk tiap request (default: 10 detik)")

    args = parser.parse_args()

    # Baca file wordlist
    with open(args.wordlist, 'r') as file:
        subdomains = file.read().splitlines()

    # Jalankan validasi
    validate_subdomains(subdomains, base_url=args.url, threads=args.threads, timeout=args.timeout)

    # Cetak hasil akhir
    print_summary()

if __name__ == "__main__":
    main()

