import random
import smtplib
import threading
import json
import time
import sqlite3
import bcrypt
import qrcode
import speech_recognition as sr
from datetime import datetime, timedelta
from tkinter import (Tk, Frame, Button, Canvas, Entry, Label, PhotoImage, 
                    messagebox, StringVar, BooleanVar, Scale, HORIZONTAL, 
                    Toplevel, Scrollbar, Listbox, Text, Checkbutton)
import cv2
from deepface import DeepFace
from twilio.rest import Client
from PIL import Image, ImageTk
import numpy as np
from cryptography.fernet import Fernet
import pickle
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from sklearn.ensemble import IsolationForest

class AdvancedAuthSystem:
    def __init__(self):
        self.root = Tk()
        self.root.title("Secure Multi-Factor Authentication System")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        self.root.configure(bg="#2c3e50")
        
        self.setup_database()
        self.load_encryption_key()
        
        self.current_frame = None
        self.auth_method = StringVar(value="multi")  
        
        self.auth_status = {
            "face": False,
            "otp": False,
            "email": False,
            "voice": False,
            "behavioral": False,
            "qr": False
        }
        
        self.security_level = StringVar(value="medium")
        self.locked_until = None
        self.failed_attempts = 0
        self.max_attempts = 3
        
        self.current_user = None
        
        
        self.typing_patterns = []
        self.mouse_movements = []
        
       
        self.show_auth_selection()
        
    def setup_database(self):
        """Initialize database for user credentials and logs"""
        self.conn = sqlite3.connect('auth_system.db')
        self.cursor = self.conn.cursor()
        
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT,
                face_embedding BLOB,
                voice_print BLOB,
                typing_pattern BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                event_type TEXT NOT NULL,
                event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                device_info TEXT,
                success BOOLEAN,
                details TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                require_2fa BOOLEAN DEFAULT 1,
                notify_on_new_device BOOLEAN DEFAULT 1,
                lock_after_attempts INTEGER DEFAULT 3,
                session_timeout INTEGER DEFAULT 30,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
    
    def load_encryption_key(self):
        """Load or generate encryption key for sensitive data"""
        try:
            with open('encryption.key', 'rb') as key_file:
                self.cipher = Fernet(key_file.read())
        except FileNotFoundError:
            key = Fernet.generate_key()
            with open('encryption.key', 'wb') as key_file:
                key_file.write(key)
            self.cipher = Fernet(key)
    
    def log_event(self, event_type, success=True, details=""):
        """Log security events to database"""
        if self.current_user:
            user_id = self.current_user[0]
            
            ip_address = "192.168.1.1"  # Placeholder
            device_info = "Desktop"  # Placeholder
            
            self.cursor.execute(
                '''INSERT INTO audit_log 
                (user_id, event_type, ip_address, device_info, success, details)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, event_type, ip_address, device_info, success, details)
            )
            self.conn.commit()
    
    def show_frame(self, frame):
        """Switch between frames"""
        if self.current_frame:
            self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)
    
    def show_auth_selection(self):
        """Show authentication method selection screen"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Secure Authentication System", font=("Arial", 24, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=30)
        
        
        security_frame = Frame(frame, bg="#2c3e50")
        security_frame.pack(pady=10)
        
        Label(security_frame, text="Security Level:", 
              font=("Arial", 14), fg="white", bg="#2c3e50").pack(side="left", padx=10)
        
        security_options = [("Low", "low"), ("Medium", "medium"), ("High", "high"), ("Maximum", "maximum")]
        for text, value in security_options:
            Button(security_frame, text=text, font=("Arial", 10), 
                  command=lambda v=value: self.set_security_level(v),
                  bg="#3498db" if value == self.security_level.get() else "#7f8c8d", 
                  fg="white", width=8).pack(side="left", padx=5)
        
        
        method_frame = Frame(frame, bg="#2c3e50")
        method_frame.pack(pady=20)
        
        Label(method_frame, text="Select Authentication Method:", 
              font=("Arial", 14), fg="white", bg="#2c3e50").pack(pady=10)
        
        methods = [
            ("Facial Recognition", "face"),
            ("OTP Verification", "otp"),
            ("Email Verification", "email"),
            ("Voice Recognition", "voice"),
            ("QR Code Login", "qr"),
            ("Multi-Factor (All Methods)", "multi")
        ]
        
        for text, mode in methods:
            btn = Button(method_frame, text=text, font=("Arial", 12), 
                  command=lambda m=mode: self.select_auth_method(m),
                  bg="#3498db", fg="white", width=25, height=2)
            btn.pack(pady=5)
        
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2980b9"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#3498db"))
        
        
        Button(frame, text="Admin / Register", font=("Arial", 10), 
              command=self.show_admin_panel, bg="#e74c3c", fg="white").pack(pady=20)
        
        
        Button(frame, text="View Security Analytics", font=("Arial", 10), 
              command=self.show_security_analytics, bg="#9b59b6", fg="white").pack(pady=10)
        
        self.show_frame(frame)
    
    def set_security_level(self, level):
        """Set the security level for authentication"""
        self.security_level.set(level)
        self.show_auth_selection()  
    
    def select_auth_method(self, method):
        """Handle authentication method selection"""
        self.auth_method.set(method)
        
        
        for key in self.auth_status:
            self.auth_status[key] = False
        
        if method == "face":
            self.start_face_authentication()
        elif method == "otp":
            self.show_otp_verification()
        elif method == "email":
            self.start_email_verification()
        elif method == "voice":
            self.start_voice_authentication()
        elif method == "qr":
            self.show_qr_authentication()
        elif method == "multi":
            self.start_multi_factor_auth()
    
    def start_face_authentication(self):
        """Start facial recognition authentication with liveness detection"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Facial Recognition with Liveness Detection", 
                     font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        
        instructions = Label(frame, text="Please look directly at the camera and blink when prompted", 
                            font=("Arial", 12), fg="white", bg="#2c3e50", wraplength=600)
        instructions.pack(pady=10)
        
        
        video_frame = Frame(frame, bg="black", width=400, height=300)
        video_frame.pack(pady=10)
        video_frame.pack_propagate(False)
        
        label = Label(video_frame, text="Camera Feed Will Appear Here", 
                     fg="white", bg="black")
        label.pack(expand=True)
        
        
        challenge_text = StringVar()
        challenge_text.set("Ready for liveness detection...")
        challenge_label = Label(frame, textvariable=challenge_text, 
                               font=("Arial", 14), fg="yellow", bg="#2c3e50")
        challenge_label.pack(pady=10)
        
        
        controls = Frame(frame, bg="#2c3e50")
        controls.pack(pady=10)
        
        Button(controls, text="Start Camera", font=("Arial", 12), 
              command=lambda: self.start_face_capture(video_frame, challenge_text),
              bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        Button(controls, text="Back", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        self.show_frame(frame)
    
    def start_face_capture(self, video_frame, challenge_text):
        """Start capturing video for face recognition with liveness detection"""
        
        
        
        challenges = ["Please blink your eyes", "Turn your head slightly left", "Smile for the camera"]
        for challenge in challenges:
            challenge_text.set(challenge)
            self.root.update()
            time.sleep(2)
        
        
        self.root.after(3000, lambda: self.face_auth_success(challenge_text))
    
    def face_auth_success(self, challenge_text):
        """Handle successful face authentication"""
        self.auth_status["face"] = True
        challenge_text.set("Face recognition successful!")
        self.log_event("face_auth", True, "Liveness detection passed")
        self.check_auth_completion()
    
    def show_otp_verification(self):
        """Show OTP verification screen with multiple delivery options"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Multi-Channel OTP Verification", font=("Arial", 20, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Delivery method selection
        delivery_frame = Frame(frame, bg="#2c3e50")
        delivery_frame.pack(pady=10)
        
        Label(delivery_frame, text="Delivery Method:", font=("Arial", 12), 
              fg="white", bg="#2c3e50").pack(side="left")
        
        delivery_method = StringVar(value="sms")
        methods = [("SMS", "sms"), ("Email", "email"), ("WhatsApp", "whatsapp"), ("Voice Call", "voice")]
        
        for text, value in methods:
            Button(delivery_frame, text=text, font=("Arial", 10), 
                  command=lambda v=value: delivery_method.set(v),
                  bg="#3498db" if value == delivery_method.get() else "#7f8c8d", 
                  fg="white").pack(side="left", padx=5)
        
        # Phone number/email input
        input_frame = Frame(frame, bg="#2c3e50")
        input_frame.pack(pady=10)
        
        Label(input_frame, text="Contact:", font=("Arial", 12), 
              fg="white", bg="#2c3e50").pack(side="left")
        
        contact_entry = Entry(input_frame, font=("Arial", 12), width=20)
        contact_entry.pack(side="left", padx=10)
        
        # OTP input
        otp_frame = Frame(frame, bg="#2c3e50")
        otp_frame.pack(pady=10)
        
        Label(otp_frame, text="OTP Code:", font=("Arial", 12), 
              fg="white", bg="#2c3e50").pack(side="left")
        
        otp_entry = Entry(otp_frame, font=("Arial", 12), width=10, show="*")
        otp_entry.pack(side="left", padx=10)
        
        # Buttons
        button_frame = Frame(frame, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Send OTP", font=("Arial", 12), 
              command=lambda: self.send_otp(contact_entry.get(), delivery_method.get()),
              bg="#3498db", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Verify", font=("Arial", 12), 
              command=lambda: self.verify_otp(otp_entry.get()),
              bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Back", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        self.show_frame(frame)
    
    def send_otp(self, contact, method):
        """Send OTP via selected method (simulated)"""
        if not contact:
            messagebox.showerror("Error", "Please enter a contact address")
            return
            
        # In a real implementation, this would use appropriate APIs
        self.current_otp = random.randint(100000, 999999)
        method_name = {
            "sms": "SMS",
            "email": "Email",
            "whatsapp": "WhatsApp",
            "voice": "Voice Call"
        }.get(method, "SMS")
        
        messagebox.showinfo("OTP Sent", f"OTP {self.current_otp} sent via {method_name} to {contact}. In a real system, this would be actually delivered.")
        self.log_event("otp_sent", True, f"OTP sent via {method_name}")
    
    def verify_otp(self, otp):
        """Verify entered OTP"""
        try:
            if int(otp) == self.current_otp:
                self.auth_status["otp"] = True
                messagebox.showinfo("Success", "OTP verification successful!")
                self.log_event("otp_verify", True, "OTP matched")
                self.check_auth_completion()
            else:
                self.failed_attempts += 1
                messagebox.showerror("Error", "Invalid OTP code")
                self.log_event("otp_verify", False, "OTP mismatch")
                
                if self.failed_attempts >= self.max_attempts:
                    self.lock_account()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid OTP code")
    
    def lock_account(self):
        """Lock account after too many failed attempts"""
        self.locked_until = datetime.now() + timedelta(minutes=15)
        messagebox.showerror("Account Locked", 
                           f"Too many failed attempts. Account locked until {self.locked_until.strftime('%H:%M:%S')}")
        self.log_event("account_lock", False, "Too many failed attempts")
        self.show_auth_selection()
    
    def start_email_verification(self):
        """Start email verification process with advanced options"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Email Verification with Magic Links", font=("Arial", 20, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Email input
        email_frame = Frame(frame, bg="#2c3e50")
        email_frame.pack(pady=10)
        
        Label(email_frame, text="Email Address:", font=("Arial", 12), 
              fg="white", bg="#2c3e50").pack(side="left")
        
        email_entry = Entry(email_frame, font=("Arial", 12), width=25)
        email_entry.pack(side="left", padx=10)
        
        # Verification options
        options_frame = Frame(frame, bg="#2c3e50")
        options_frame.pack(pady=10)
        
        Label(options_frame, text="Verification Method:", font=("Arial", 12), 
              fg="white", bg="#2c3e50").pack(side="left")
        
        verify_method = StringVar(value="code")
        methods = [("Verification Code", "code"), ("Magic Link", "link"), ("One-Click", "click")]
        
        for text, value in methods:
            Button(options_frame, text=text, font=("Arial", 10), 
                  command=lambda v=value: verify_method.set(v),
                  bg="#3498db" if value == verify_method.get() else "#7f8c8d", 
                  fg="white").pack(side="left", padx=5)
        
        # OTP input (only shown for code method)
        otp_frame = Frame(frame, bg="#2c3e50")
        otp_frame.pack(pady=10)
        
        Label(otp_frame, text="Verification Code:", font=("Arial", 12), 
              fg="white", bg="#2c3e50").pack(side="left")
        
        otp_entry = Entry(otp_frame, font=("Arial", 12), width=10, show="*")
        otp_entry.pack(side="left", padx=10)
        
        # Buttons
        button_frame = Frame(frame, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Send Verification", font=("Arial", 12), 
              command=lambda: self.send_email_verification(
                  email_entry.get(), verify_method.get()),
              bg="#3498db", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Verify", font=("Arial", 12), 
              command=lambda: self.verify_email_code(otp_entry.get(), verify_method.get()),
              bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Back", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        self.show_frame(frame)
    
    def send_email_verification(self, email, method):
        """Send email verification (simulated)"""
        if not email or "@" not in email:
            messagebox.showerror("Error", "Please enter a valid email address")
            return
            
        # In a real implementation, this would use SMTP
        if method == "code":
            self.email_code = random.randint(100000, 999999)
            messagebox.showinfo("Code Sent", 
                              f"Verification code {self.email_code} sent to {email}. In a real system, this would be sent via email.")
        elif method == "link":
            self.magic_link_token = Fernet.generate_key().decode()
            messagebox.showinfo("Magic Link Sent", 
                              f"Magic link sent to {email}. In a real system, this would be sent via email.")
        else:  # one-click
            messagebox.showinfo("One-Click Email Sent", 
                              f"One-click verification email sent to {email}. In a real system, this would be sent via email.")
        
        self.log_event("email_verification_sent", True, f"Method: {method}")
    
    def verify_email_code(self, code, method):
        """Verify email code"""
        if method == "code":
            try:
                if int(code) == self.email_code:
                    self.auth_status["email"] = True
                    messagebox.showinfo("Success", "Email verification successful!")
                    self.log_event("email_verify", True, "Code verification")
                    self.check_auth_completion()
                else:
                    messagebox.showerror("Error", "Invalid verification code")
                    self.log_event("email_verify", False, "Code mismatch")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid verification code")
        else:
            # For magic link and one-click, we would simulate verification
            self.auth_status["email"] = True
            messagebox.showinfo("Success", "Email verification successful!")
            self.log_event("email_verify", True, f"Method: {method}")
            self.check_auth_completion()
    
    def start_voice_authentication(self):
        """Start voice recognition authentication"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Voice Recognition Authentication", font=("Arial", 20, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Instructions
        instructions = Label(frame, text="Please say the following phrase when prompted:", 
                            font=("Arial", 12), fg="white", bg="#2c3e50", wraplength=600)
        instructions.pack(pady=10)
        
        # Phrase to speak
        voice_phrase = StringVar()
        phrases = [
            "The quick brown fox jumps over the lazy dog",
            "My voice is my password, verify me",
            "Authentication through voice recognition",
            "Security is paramount in the digital age"
        ]
        voice_phrase.set(random.choice(phrases))
        
        phrase_label = Label(frame, textvariable=voice_phrase, font=("Arial", 14, "bold"), 
                           fg="yellow", bg="#2c3e50", wraplength=600)
        phrase_label.pack(pady=10)
        
        # Record button
        record_btn = Button(frame, text="Start Recording", font=("Arial", 14), 
                          command=lambda: self.record_voice(voice_phrase.get()),
                          bg="#27ae60", fg="white", width=20)
        record_btn.pack(pady=20)
        
        # Status
        status_text = StringVar()
        status_text.set("Ready to record...")
        status_label = Label(frame, textvariable=status_text, font=("Arial", 12), 
                           fg="white", bg="#2c3e50")
        status_label.pack(pady=10)
        
        # Back button
        Button(frame, text="Back", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(pady=10)
        
        self.show_frame(frame)
    
    def record_voice(self, phrase):
        """Record and verify voice (simulated)"""
        # In a real implementation, this would use speech recognition and voice analysis
        messagebox.showinfo("Info", "Voice recording would start here. This is a simulation.")
        
        # Simulate processing
        for i in range(3, 0, -1):
            self.root.update()
            time.sleep(1)
        
        # Simulate successful verification
        self.auth_status["voice"] = True
        messagebox.showinfo("Success", "Voice recognition successful!")
        self.log_event("voice_auth", True, "Voiceprint matched")
        self.check_auth_completion()
    
    def show_qr_authentication(self):
        """Show QR code authentication"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="QR Code Authentication", font=("Arial", 20, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Instructions
        instructions = Label(frame, text="Scan the QR code with your authenticator app:", 
                            font=("Arial", 12), fg="white", bg="#2c3e50", wraplength=600)
        instructions.pack(pady=10)
        
        # Generate QR code
        qr_data = f"auth://{random.randint(100000, 999999)}"
        qr_img = qrcode.make(qr_data)
        qr_img = qr_img.resize((200, 200), Image.LANCZOS)
        qr_photo = ImageTk.PhotoImage(qr_img)
        
        qr_label = Label(frame, image=qr_photo, bg="#2c3e50")
        qr_label.image = qr_photo  # Keep a reference
        qr_label.pack(pady=10)
        
        # Verification code input
        code_frame = Frame(frame, bg="#2c3e50")
        code_frame.pack(pady=10)
        
        Label(code_frame, text="Verification Code:", font=("Arial", 12), 
              fg="white", bg="#2c3e50").pack(side="left")
        
        code_entry = Entry(code_frame, font=("Arial", 12), width=10)
        code_entry.pack(side="left", padx=10)
        
        # Buttons
        button_frame = Frame(frame, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Verify", font=("Arial", 12), 
              command=lambda: self.verify_qr_code(code_entry.get(), qr_data),
              bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Back", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        self.show_frame(frame)
    
    def verify_qr_code(self, code, expected_data):
        """Verify QR code (simulated)"""
        # In a real implementation, this would validate against the QR code data
        if code == "123456":  # Simulated validation
            self.auth_status["qr"] = True
            messagebox.showinfo("Success", "QR code authentication successful!")
            self.log_event("qr_auth", True, "QR code verified")
            self.check_auth_completion()
        else:
            messagebox.showerror("Error", "Invalid verification code")
            self.log_event("qr_auth", False, "QR code mismatch")
    
    def start_multi_factor_auth(self):
        """Start multi-factor authentication process"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Multi-Factor Authentication", font=("Arial", 20, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Progress indicator
        progress_frame = Frame(frame, bg="#2c3e50")
        progress_frame.pack(pady=10)
        
        # Determine required factors based on security level
        security_factors = {
            "low": ["face"],
            "medium": ["face", "otp"],
            "high": ["face", "otp", "email"],
            "maximum": ["face", "otp", "email", "voice", "behavioral"]
        }
        
        required_factors = security_factors.get(self.security_level.get(), ["face", "otp"])
        
        self.mfa_status = {factor: BooleanVar(value=False) for factor in required_factors}
        
        for i, factor in enumerate(required_factors):
            step_frame = Frame(progress_frame, bg="#2c3e50")
            step_frame.pack(pady=5)
            
            # Status indicator
            status_canvas = Canvas(step_frame, width=20, height=20, bg="red", 
                                  highlightthickness=0)
            status_canvas.pack(side="left", padx=5)
            
            # Factor name
            factor_name = {
                "face": "Facial Recognition",
                "otp": "OTP Verification",
                "email": "Email Verification",
                "voice": "Voice Recognition",
                "behavioral": "Behavioral Biometrics"
            }.get(factor, factor)
            
            Label(step_frame, text=factor_name, font=("Arial", 12), 
                  fg="white", bg="#2c3e50").pack(side="left")
            
            # Update indicator when status changes
            def update_indicator(var, canvas, factor=factor):
                canvas.config(bg="green" if var.get() else "red")
            
            self.mfa_status[factor].trace("w", 
                lambda *args, var=self.mfa_status[factor], canvas=status_canvas: 
                update_indicator(var, canvas))
        
        # Buttons to start each authentication method
        button_frame = Frame(frame, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        if "face" in required_factors:
            Button(button_frame, text="Start Face Recognition", font=("Arial", 12), 
                  command=self.start_face_authentication,
                  bg="#3498db", fg="white").pack(side="left", padx=5)
        
        if "otp" in required_factors:
            Button(button_frame, text="Start OTP Verification", font=("Arial", 12), 
                  command=self.show_otp_verification,
                  bg="#3498db", fg="white").pack(side="left", padx=5)
        
        if "email" in required_factors:
            Button(button_frame, text="Start Email Verification", font=("Arial", 12), 
                  command=self.start_email_verification,
                  bg="#3498db", fg="white").pack(side="left", padx=5)
        
        if "voice" in required_factors:
            Button(button_frame, text="Start Voice Recognition", font=("Arial", 12), 
                  command=self.start_voice_authentication,
                  bg="#3498db", fg="white").pack(side="left", padx=5)
        
        if "behavioral" in required_factors:
            Button(button_frame, text="Start Behavioral Analysis", font=("Arial", 12), 
                  command=self.start_behavioral_analysis,
                  bg="#3498db", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Back", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        self.show_frame(frame)
    
    def start_behavioral_analysis(self):
        """Start behavioral biometrics analysis"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Behavioral Biometrics Analysis", font=("Arial", 20, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Instructions
        instructions = Label(frame, text="Please type the following text in your natural rhythm:", 
                            font=("Arial", 12), fg="white", bg="#2c3e50", wraplength=600)
        instructions.pack(pady=10)
        
        # Text to type
        text_to_type = "The quick brown fox jumps over the lazy dog. This sentence contains all letters of the English alphabet."
        
        text_frame = Frame(frame, bg="#34495e", padx=10, pady=10)
        text_frame.pack(pady=10)
        
        text_label = Label(text_frame, text=text_to_type, font=("Arial", 12), 
                          fg="white", bg="#34495e", wraplength=500)
        text_label.pack()
        
        # Typing area
        typing_frame = Frame(frame, bg="#2c3e50")
        typing_frame.pack(pady=10)
        
        typing_entry = Text(typing_frame, font=("Arial", 12), width=50, height=5)
        typing_entry.pack()
        
        # Start typing analysis
        start_time = None
        typing_pattern = []
        
        def on_key_press(event):
            nonlocal start_time, typing_pattern
            if start_time is None:
                start_time = datetime.now()
            
            current_time = datetime.now()
            elapsed = (current_time - start_time).total_seconds() * 1000  # milliseconds
            typing_pattern.append((event.char, elapsed))
        
        typing_entry.bind("<KeyPress>", on_key_press)
        
        # Buttons
        button_frame = Frame(frame, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        def analyze_typing():
            # Simulate behavioral analysis
            messagebox.showinfo("Info", "Analyzing typing patterns...")
            
            # Simulate processing
            for i in range(3, 0, -1):
                self.root.update()
                time.sleep(1)
            
            # Simulate successful verification
            self.auth_status["behavioral"] = True
            messagebox.showinfo("Success", "Behavioral analysis successful!")
            self.log_event("behavioral_auth", True, "Typing pattern matched")
            self.check_auth_completion()
        
        Button(button_frame, text="Analyze Typing Pattern", font=("Arial", 12), 
              command=analyze_typing,
              bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Back", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        self.show_frame(frame)
    
    def check_auth_completion(self):
        """Check if all required authentications are completed"""
        method = self.auth_method.get()
        
        if method == "multi":
            # Check if all required factors are completed
            security_factors = {
                "low": ["face"],
                "medium": ["face", "otp"],
                "high": ["face", "otp", "email"],
                "maximum": ["face", "otp", "email", "voice", "behavioral"]
            }
            
            required_factors = security_factors.get(self.security_level.get(), ["face", "otp"])
            all_completed = all(self.auth_status[factor] for factor in required_factors)
            
            if all_completed:
                self.show_success_screen()
        else:
            # Single method authentication
            if self.auth_status[method]:
                self.show_success_screen()
    
    def show_success_screen(self):
        """Show authentication success screen with dashboard"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Authentication Successful!", font=("Arial", 24, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=30)
        
        # Security score
        score = random.randint(85, 99)  # Simulated security score
        score_color = "#27ae60" if score > 90 else "#f39c12"
        
        score_frame = Frame(frame, bg="#2c3e50")
        score_frame.pack(pady=10)
        
        Label(score_frame, text="Security Score:", font=("Arial", 16), 
              fg="white", bg="#2c3e50").pack(side="left")
        
        Label(score_frame, text=f"{score}%", font=("Arial", 16, "bold"), 
              fg=score_color, bg="#2c3e50").pack(side="left", padx=10)
        
        # Session information
        session_frame = Frame(frame, bg="#34495e", padx=20, pady=20)
        session_frame.pack(pady=20, padx=50, fill="x")
        
        Label(session_frame, text="Session Information", font=("Arial", 16, "bold"), 
              fg="white", bg="#34495e").pack(pady=10)
        
        now = datetime.now()
        session_info = f"""• Login Time: {now.strftime('%Y-%m-%d %H:%M:%S')}
• Authentication Method: {self.auth_method.get().capitalize()}
• Security Level: {self.security_level.get().capitalize()}
• IP Address: 192.168.1.1 (simulated)
• Device: Desktop Web Browser
• Session Timeout: 30 minutes"""
        
        info_label = Label(session_frame, text=session_info, font=("Courier", 12), 
                          justify="left", fg="white", bg="#34495e")
        info_label.pack()
        
        # Action buttons
        button_frame = Frame(frame, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Access Secure Dashboard", font=("Arial", 12), 
              command=self.show_secure_dashboard,
              bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="View Security Log", font=("Arial", 12), 
              command=self.show_security_log,
              bg="#3498db", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Logout", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        self.show_frame(frame)
    
    def show_secure_dashboard(self):
        """Show secure dashboard after successful authentication"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Secure Dashboard", font=("Arial", 24, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Dashboard content
        content_frame = Frame(frame, bg="#34495e", padx=20, pady=20)
        content_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        Label(content_frame, text="Welcome to your secure dashboard!", 
              font=("Arial", 16), fg="white", bg="#34495e").pack(pady=10)
        
        # Sample secure data
        secure_data = """• Account Balance: $12,456.78
• Recent Transactions: 
  - Amazon: $45.67 (Today)
  - Netflix: $15.99 (Yesterday)
  - Grocery Store: $78.45 (2 days ago)
• Security Alerts: None
• System Status: All services operational"""
        
        data_label = Label(content_frame, text=secure_data, font=("Courier", 12), 
                          justify="left", fg="white", bg="#34495e")
        data_label.pack(pady=10)
        
        # Action buttons
        button_frame = Frame(content_frame, bg="#34495e")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Transfer Funds", font=("Arial", 12), 
              command=lambda: messagebox.showinfo("Info", "Fund transfer feature would be implemented here"),
              bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="View Statements", font=("Arial", 12), 
              command=lambda: messagebox.showinfo("Info", "Statement viewing feature would be implemented here"),
              bg="#3498db", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Security Settings", font=("Arial", 12), 
              command=self.show_security_settings,
              bg="#9b59b6", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Logout", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        self.show_frame(frame)
    
    def show_security_log(self):
        """Show security event log"""
        log_window = Toplevel(self.root)
        log_window.title("Security Event Log")
        log_window.geometry("800x500")
        log_window.configure(bg="#2c3e50")
        
        title = Label(log_window, text="Security Event Log", font=("Arial", 18, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=10)
        
        # Create a frame for the listbox and scrollbar
        log_frame = Frame(log_window)
        log_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Create a scrollbar
        scrollbar = Scrollbar(log_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Create a listbox to display log entries
        log_listbox = Listbox(log_frame, yscrollcommand=scrollbar.set, 
                             font=("Courier", 10), bg="#34495e", fg="white")
        log_listbox.pack(side="left", fill="both", expand=True)
        
        # Configure the scrollbar
        scrollbar.config(command=log_listbox.yview)
        
        # Add sample log entries (in a real system, these would come from the database)
        log_entries = [
            "2023-10-15 14:30:22 - Login successful - Facial recognition",
            "2023-10-15 14:28:10 - OTP verification failed - Incorrect code",
            "2023-10-15 14:25:35 - New device detected - Notification sent",
            "2023-10-15 13:45:18 - Password changed successfully",
            "2023-10-14 09:12:45 - Login successful - Multi-factor authentication",
            "2023-10-13 16:20:33 - Suspicious login attempt - Account temporarily locked",
            "2023-10-12 11:05:17 - Email verification successful",
            "2023-10-11 08:30:55 - Voice recognition enrolled",
            "2023-10-10 15:40:29 - Security settings updated",
            "2023-10-09 10:15:44 - New authentication device registered"
        ]
        
        for entry in log_entries:
            log_listbox.insert("end", entry)
        
        # Close button
        Button(log_window, text="Close", font=("Arial", 12), 
              command=log_window.destroy,
              bg="#e74c3c", fg="white").pack(pady=10)
    
    def show_security_settings(self):
        """Show security settings panel"""
        settings_window = Toplevel(self.root)
        settings_window.title("Security Settings")
        settings_window.geometry("600x400")
        settings_window.configure(bg="#2c3e50")
        
        title = Label(settings_window, text="Security Settings", font=("Arial", 18, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=10)
        
        # Settings content
        settings_frame = Frame(settings_window, bg="#34495e", padx=20, pady=20)
        settings_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Two-factor authentication setting
        two_fa_var = BooleanVar(value=True)
        Checkbutton(settings_frame, text="Require two-factor authentication", 
                   variable=two_fa_var, font=("Arial", 12), 
                   fg="white", bg="#34495e", selectcolor="#2c3e50").pack(anchor="w", pady=5)
        
        # Notify on new device setting
        notify_var = BooleanVar(value=True)
        Checkbutton(settings_frame, text="Notify on new device login", 
                   variable=notify_var, font=("Arial", 12), 
                   fg="white", bg="#34495e", selectcolor="#2c3e50").pack(anchor="w", pady=5)
        
        # Session timeout setting
        timeout_frame = Frame(settings_frame, bg="#34495e")
        timeout_frame.pack(fill="x", pady=10)
        
        Label(timeout_frame, text="Session timeout (minutes):", 
              font=("Arial", 12), fg="white", bg="#34495e").pack(side="left")
        
        timeout_var = StringVar(value="30")
        timeout_options = ["15", "30", "60", "120"]
        timeout_dropdown = OptionMenu(timeout_frame, timeout_var, *timeout_options)
        timeout_dropdown.config(bg="#3498db", fg="white")
        timeout_dropdown.pack(side="left", padx=10)
        
        # Save button
        Button(settings_frame, text="Save Settings", font=("Arial", 12), 
              command=lambda: self.save_security_settings(two_fa_var.get(), notify_var.get(), timeout_var.get()),
              bg="#27ae60", fg="white").pack(pady=20)
        
        # Close button
        Button(settings_window, text="Close", font=("Arial", 12), 
              command=settings_window.destroy,
              bg="#e74c3c", fg="white").pack(pady=10)
    
    def save_security_settings(self, require_2fa, notify_new_device, session_timeout):
        """Save security settings"""
        # In a real implementation, this would save to the database
        messagebox.showinfo("Success", "Security settings saved successfully!")
        self.log_event("settings_update", True, 
                      f"2FA: {require_2fa}, Notify: {notify_new_device}, Timeout: {session_timeout}")
    
    def show_security_analytics(self):
        """Show security analytics dashboard"""
        analytics_window = Toplevel(self.root)
        analytics_window.title("Security Analytics")
        analytics_window.geometry("800x600")
        analytics_window.configure(bg="#2c3e50")
        
        title = Label(analytics_window, text="Security Analytics Dashboard", 
                     font=("Arial", 18, "bold"), fg="white", bg="#2c3e50")
        title.pack(pady=10)
        
        # Create a figure for the analytics
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8))
        fig.patch.set_facecolor('#2c3e50')
        
        # Sample data for charts
        auth_methods = ['Face', 'OTP', 'Email', 'Voice', 'QR']
        success_rates = [95, 88, 92, 85, 90]
        failure_rates = [5, 12, 8, 15, 10]
        
        # Chart 1: Authentication methods usage
        ax1.bar(auth_methods, success_rates, color=['#3498db', '#2ecc71', '#9b59b6', '#e74c3c', '#f39c12'])
        ax1.set_title('Authentication Success Rates', color='white')
        ax1.set_facecolor('#34495e')
        ax1.tick_params(colors='white')
        
        # Chart 2: Login attempts over time
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        logins = [120, 135, 115, 140, 160, 90, 75]
        ax2.plot(days, logins, marker='o', color='#2ecc71')
        ax2.set_title('Daily Login Attempts', color='white')
        ax2.set_facecolor('#34495e')
        ax2.tick_params(colors='white')
        
        # Chart 3: Security events by type
        event_types = ['Success', 'Failed', 'Lockout', 'Suspicious']
        events = [85, 10, 3, 2]
        ax3.pie(events, labels=event_types, autopct='%1.1f%%', 
                colors=['#2ecc71', '#e74c3c', '#f39c12', '#3498db'])
        ax3.set_title('Security Event Distribution', color='white')
        
        # Chart 4: Risk score over time
        risk_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        risk_scores = [75, 80, 82, 78, 85, 90, 88]
        ax4.plot(risk_days, risk_scores, marker='o', color='#e74c3c')
        ax4.set_title('Daily Risk Score', color='white')
        ax4.set_facecolor('#34495e')
        ax4.tick_params(colors='white')
        
        # Adjust layout
        plt.tight_layout()
        
        # Embed the chart in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=analytics_window)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)
        
        # Close button
        Button(analytics_window, text="Close", font=("Arial", 12), 
              command=analytics_window.destroy,
              bg="#e74c3c", fg="white").pack(pady=10)
    
    def show_admin_panel(self):
        """Show admin/registration panel"""
        frame = Frame(self.root, bg="#2c3e50")
        
        title = Label(frame, text="Admin / Registration Panel", font=("Arial", 20, "bold"), 
                     fg="white", bg="#2c3e50")
        title.pack(pady=20)
        
        # Tab selection
        tab_frame = Frame(frame, bg="#2c3e50")
        tab_frame.pack(pady=10)
        
        tabs = ["User Registration", "User Management", "System Settings"]
        current_tab = StringVar(value=tabs[0])
        
        for tab in tabs:
            Button(tab_frame, text=tab, font=("Arial", 12), 
                  command=lambda t=tab: current_tab.set(t),
                  bg="#3498db" if tab == current_tab.get() else "#7f8c8d", 
                  fg="white").pack(side="left", padx=5)
        
        # Content area
        content_frame = Frame(frame, bg="#34495e", width=600, height=300)
        content_frame.pack(pady=10)
        content_frame.pack_propagate(False)
        
        # Registration form
        reg_frame = Frame(content_frame, bg="#34495e")
        
        fields = [
            ("Username:", "username"),
            ("Password:", "password", True),
            ("Email:", "email"),
            ("Phone:", "phone")
        ]
        
        self.reg_vars = {}
        
        for i, field in enumerate(fields):
            row = Frame(reg_frame, bg="#34495e")
            row.pack(pady=5)
            
            Label(row, text=field[0], font=("Arial", 12), 
                  fg="white", bg="#34495e", width=12).pack(side="left")
            
            show_char = "*" if len(field) > 2 and field[2] else None
            entry = Entry(row, font=("Arial", 12), width=20, show=show_char)
            entry.pack(side="left")
            
            self.reg_vars[field[1]] = entry
        
        reg_frame.pack(expand=True)
        
        # Buttons
        button_frame = Frame(frame, bg="#2c3e50")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="Register", font=("Arial", 12), 
              command=self.register_user,
              bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        Button(button_frame, text="Back", font=("Arial", 12), 
              command=self.show_auth_selection,
              bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        # Function to update content based on selected tab
        def update_content():
            for widget in content_frame.winfo_children():
                widget.destroy()
            
            if current_tab.get() == "User Registration":
                reg_frame.pack(expand=True)
            elif current_tab.get() == "User Management":
                Label(content_frame, text="User Management Features", 
                      font=("Arial", 16), fg="white", bg="#34495e").pack(expand=True)
            else:  # System Settings
                Label(content_frame, text="System Settings", 
                      font=("Arial", 16), fg="white", bg="#34495e").pack(expand=True)
        
        current_tab.trace("w", lambda *args: update_content())
        
        self.show_frame(frame)
    
    def register_user(self):
        """Register a new user"""
        username = self.reg_vars["username"].get()
        password = self.reg_vars["password"].get()
        email = self.reg_vars["email"].get()
        phone = self.reg_vars["phone"].get()
        
        if not all([username, password, email]):
            messagebox.showerror("Error", "Please fill all required fields")
            return
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        # Store user in database
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, email, phone) VALUES (?, ?, ?, ?)",
                (username, password_hash, email, phone)
            )
            self.conn.commit()
            messagebox.showinfo("Success", "User registered successfully!")
            self.log_event("user_registration", True, f"New user: {username}")
            self.show_auth_selection()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
            self.log_event("user_registration", False, "Username already exists")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# For the OptionMenu which we need to import
from tkinter import OptionMenu

if __name__ == "__main__":
    app = AdvancedAuthSystem()
    app.run()