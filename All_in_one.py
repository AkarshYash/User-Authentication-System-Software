import random
import smtplib
import threading
from datetime import datetime, timedelta
from tkinter import Button, Canvas, Entry, Label, PhotoImage, Tk, messagebox

import cv2
from deepface import DeepFace
from twilio.rest import Client


# Video-based Face Matching System
class FaceMatcher:
    def __init__(self, reference_image_path):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.reference_img = cv2.imread(reference_image_path)
        self.counter = 0
        self.face_match = False

    def check_face(self, frame):
        try:
            self.face_match = DeepFace.verify(frame, self.reference_img.copy())["verified"]
        except Exception:
            self.face_match = False

    def start(self):
        while True:
            ret, frame = self.cap.read()
            if ret:
                if self.counter % 30 == 0:
                    threading.Thread(target=self.check_face, args=(frame.copy(),)).start()
                
                self.counter += 1
                text = "MATCH!" if self.face_match else "NO MATCH!"
                color = (0, 255, 0) if self.face_match else (0, 0, 255)
                cv2.putText(frame, text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 3)
                cv2.imshow("Video", frame)

            if cv2.waitKey(1) == ord("q"):
                break

        self.cap.release()
        cv2.destroyAllWindows()

# OTP Verification System with Twilio and Email Support
class OTPVerifier(Tk):
    def __init__(self):
        super().__init__()
        self.geometry("600x550")
        self.resizable(False, False)
        self.otp = random.randint(1000, 9999)
        self.client = Client("YOUR_TWILIO_SID", "YOUR_TWILIO_AUTH_TOKEN")
        self.client.messages.create(
            to="YOUR_PHONE_NUMBER", from_="YOUR_TWILIO_PHONE_NUMBER", body=str(self.otp)
        )

    def labels(self):
        self.c = Canvas(self, bg="white", width=400, height=280)
        self.c.place(x=100, y=60)
        self.login_title = Label(self, text="OTP Verification", font=("bold", 20), bg="white")
        self.login_title.place(x=210, y=90)

    def entry(self):
        self.user_name = Entry(self, borderwidth=2)
        self.user_name.place(x=190, y=160)

    def buttons(self):
        self.submitbutton = Button(self, text="Submit", command=self.check_otp)
        self.submitbutton.place(x=208, y=400)

        self.resendotp = Button(self, text="Resend OTP", command=self.resend_otp)
        self.resendotp.place(x=208, y=450)

    def check_otp(self):
        try:
            user_input = int(self.user_name.get())
            if user_input == self.otp:
                messagebox.showinfo("Info", "Login successful")
                self.otp = "done"
            elif self.otp == "done":
                messagebox.showinfo("Info", "Already logged in")
            else:
                messagebox.showinfo("Info", "Wrong OTP")
        except ValueError:
            messagebox.showinfo("Info", "Invalid OTP")

    def resend_otp(self):
        self.otp = random.randint(1000, 9999)
        self.client.messages.create(
            to="YOUR_PHONE_NUMBER", from_="YOUR_TWILIO_PHONE_NUMBER", body=str(self.otp)
        )

# Email Verification with Retry and Blocking System
class EmailVerification:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "youremail@example.com"
        self.sender_password = "yourpassword"
        self.otp_storage = {}
        self.attempts = {}
        self.blocked_emails = {}

    def send_otp(self, email, otp):
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                subject = "Your OTP for Verification"
                message = f"Subject: {subject}\n\nYour OTP is: {otp}\nIt is valid for 5 minutes."
                server.sendmail(self.sender_email, email, message)
                print(f"OTP sent to {email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def is_blocked(self, email):
        if email in self.blocked_emails:
            if datetime.now() > self.blocked_emails[email]:
                del self.blocked_emails[email]
                return False
            return True
        return False

    def generate_otp(self, email):
        otp = random.randint(100000, 999999)
        self.otp_storage[email] = {"otp": otp, "expires_at": datetime.now() + timedelta(minutes=5)}
        self.send_otp(email, otp)

    def verify_email(self):
        email = input("Enter your email address: ")

        if self.is_blocked(email):
            print("Your email is blocked due to multiple failed attempts. Try again after 24 hours.")
            return

        if email not in self.attempts:
            self.attempts[email] = 0

        self.generate_otp(email)
        for _ in range(3):
            user_otp = input("Enter the OTP sent to your email: ")
            if email in self.otp_storage:
                otp_data = self.otp_storage[email]
                if datetime.now() > otp_data["expires_at"]:
                    print("OTP expired. Please request a new one.")
                    break
                if int(user_otp) == otp_data["otp"]:
                    print("Email verified successfully!")
                    del self.otp_storage[email]
                    self.attempts[email] = 0
                    return
                else:
                    print("Invalid OTP. Try again.")
                    self.attempts[email] += 1

        if self.attempts[email] >= 3:
            print("Too many failed attempts. Your email is now blocked for 24 hours.")
            self.blocked_emails[email] = datetime.now() + timedelta(hours=24)

# Example Usage
if __name__ == "__main__":
    # Start the face matcher
    face_matcher = FaceMatcher("photo.jpg")
    threading.Thread(target=face_matcher.start).start()

    # Start the OTP verification GUI
    otp_verifier = OTPVerifier()
    otp_verifier.labels()
    otp_verifier.entry()
    otp_verifier.buttons()
    otp_verifier.mainloop()

    # Start the email verification system
    email_verification = EmailVerification()
    email_verification.verify_email()
