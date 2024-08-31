import requests
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import argparse
import signal
import sys
import os

# File to store PID
PID_FILE = "background_job.pid"

# Gmail SMTP configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = st.secrets["email"]
EMAIL_PASSWORD = st.secrets["pass"]

def send_email(subject, body, recipient_email):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient_email, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {str(e)}")

def check_website(website, product_type, price, recipient_email):
    if website == "Water When Dry":
        url = "https://waterwhendry.com/products.json"
    elif website == "Kith":
        url = "https://kith.com/products.json"
    else:
        print(f"Invalid website: {website}")
        return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            new_products = []
            
            for product in data['products']:
                if product['product_type'] == product_type and any(variant['price'] == price for variant in product['variants']):
                    new_products.append({
                        'title': product['title'],
                        'handle': product['handle'],
                        'available': any(variant['available'] for variant in product['variants'])
                    })
            
            if new_products:
                result = f"Products found on {website} at {time.ctime()}:\n"
                for product in new_products:
                    availability = "Available" if product['available'] else "Sold Out"
                    result += f"- {product['title']} ({availability})\n"
                    result += f"  URL: https://{website.lower().replace(' ', '')}.com/products/{product['handle']}\n"
                send_email(f"New Products Found on {website}", result, recipient_email)
            else:
                print(f"No products matching criteria found on {website} at {time.ctime()}")
        
        elif response.status_code == 401:
            print(f"Authentication failed for {website} at {time.ctime()}. Status code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
        
        else:
            print(f"Website check failed for {website} at {time.ctime()}. Status code: {response.status_code}")
    
    except Exception as e:
        print(f"Error occurred at {time.ctime()}: {str(e)}")

def signal_handler(sig, frame):
    print("Terminating background job.")
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check product availability")
    parser.add_argument("website", help="Website to check (Water When Dry or Kith)")
    parser.add_argument("product_type", help="Product type to check")
    parser.add_argument("price", help="Price to check")
    parser.add_argument("email", help="Email address to send notifications")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    with open(PID_FILE, 'w') as pid_file:
        pid_file.write(str(os.getpid()))

    try:
        if args.once:
            check_website(args.website, args.product_type, args.price, args.email)
        else:
            while True:
                check_website(args.website, args.product_type, args.price, args.email)
                time.sleep(60)  # Sleep for 60 seconds
    finally:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
