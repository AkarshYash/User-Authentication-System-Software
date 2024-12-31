import random
import smtplib
from datetime import datetime, timedelta

# Email configuration
SENDER_EMAIL = "youremail@example.com"  # Replace with your sender email
SENDER_PASSWORD = "yourpassword"  # Replace with your sender email password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Store OTPs, attempts, and blocked emails
otp_storage = {}
attempts = {}
blocked_emails = {}

# Function to send OTP
def send_otp(email, otp):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            subject = "Your OTP for Verification"
            message = f"Subject: {subject}\n\nYour OTP is: {otp}\nIt is valid for 5 minutes."
            server.sendmail(SENDER_EMAIL, email, message)
            print(f"OTP sent to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to check if an email is blocked
def is_blocked(email):
    if email in blocked_emails:
        if datetime.now() > blocked_emails[email]:  # Check if block duration is over
            del blocked_emails[email]
            return False
        return True
    return False

# Function to generate OTP
def generate_otp(email):
    otp = random.randint(100000, 999999)
    otp_storage[email] = {'otp': otp, 'expires_at': datetime.now() + timedelta(minutes=5)}
    send_otp(email, otp)

# Main email verification system
def email_verification_system():
    while True:
        email = input("Enter your email address: ")
        
        if is_blocked(email):
            print("Your email is blocked due to multiple failed attempts. Try again after 24 hours.")
            continue
        
        if email not in attempts:
            attempts[email] = 0

        generate_otp(email)
        for _ in range(3):  # Allow up to 3 attempts
            user_otp = input("Enter the OTP sent to your email: ")
            if email in otp_storage:
                otp_data = otp_storage[email]
                if datetime.now() > otp_data['expires_at']:
                    print("OTP expired. Please request a new one.")
                    break
                if int(user_otp) == otp_data['otp']:
                    print("Email verified successfully!")
                    del otp_storage[email]
                    attempts[email] = 0  # Reset attempts on success
                    return
                else:
                    print("Invalid OTP. Try again.")
                    attempts[email] += 1

        if attempts[email] >= 3:
            print("Too many failed attempts. Your email is now blocked for 24 hours.")
            blocked_emails[email] = datetime.now() + timedelta(hours=24)

# Run the system
email_verification_system()