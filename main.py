import time
from scanner.apex_scanner import ApexScanner

while True:

    print("\n=== NEW SCAN ===")

    try:

        scanner = ApexScanner()

        scanner.run()

    except Exception as e:

        print(f"ERROR: {e}")

    print("Sleeping 30 seconds...")

    time.sleep(30)