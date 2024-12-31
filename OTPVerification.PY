import random
from tkinter import *
from tkinter import messagebox

from twilio.rest import Client


class OTPVerifier(Tk):
    def __init__(self):
        super().__init__()
        self.geometry("600x550")
        self.resizable(False, False)
        self.title("OTP Verification System")
        
        # Generate initial OTP
        self.n = random.randint(1000, 9999)
        
        # Twilio credentials
        self.client = Client("************************", "**************************")
        self.send_otp()

    def send_otp(self):
        """Send OTP to the user."""
        try:
            self.client.messages.create(
                to="+78888888888888888884",  # Replace with the user's phone number
                from_="+14176412180",  # Replace with your Twilio phone number
                body=f"Your OTP is {self.n}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send OTP: {e}")

    def labels(self):
        """Set up labels."""
        self.canvas = Canvas(self, bg="white", width=400, height=280)
        self.canvas.place(x=100, y=60)

        self.login_title = Label(self, text="OTP Verification", font=("Helvetica", 20, "bold"), bg="white")
        self.login_title.place(x=180, y=80)

        self.instruction = Label(self, text="Enter the OTP sent to your phone", font=("Helvetica", 12), bg="white")
        self.instruction.place(x=180, y=120)

    def entry(self):
        """Set up entry fields."""
        self.otp_entry = Entry(self, font=("Helvetica", 14), borderwidth=2, justify="center")
        self.otp_entry.place(x=190, y=200, width=200, height=30)

    def buttons(self):
        """Set up buttons."""
        self.submit_button = Button(self, text="Submit OTP", font=("Helvetica", 12), command=self.check_otp, bg="#4CAF50", fg="white")
        self.submit_button.place(x=190, y=250, width=200, height=40)

        self.resend_button = Button(self, text="Resend OTP", font=("Helvetica", 12), command=self.resend_otp, bg="#f44336", fg="white")
        self.resend_button.place(x=190, y=310, width=200, height=40)

    def check_otp(self):
        """Check if entered OTP is correct."""
        try:
            user_input = self.otp_entry.get()
            if not user_input:
                messagebox.showwarning("Warning", "Please enter the OTP!")
                return
            
            user_input = int(user_input)
            if user_input == self.n:
                messagebox.showinfo("Success", "Login successful!")
                self.n = "done"  # Mark OTP as used
            elif self.n == "done":
                messagebox.showinfo("Info", "Already logged in!")
            else:
                messagebox.showerror("Error", "Incorrect OTP. Try again.")
        except ValueError:
            messagebox.showerror("Error", "Invalid OTP. Please enter numeric values only.")

    def resend_otp(self):
        """Resend a new OTP."""
        self.n = random.randint(1000, 9999)
        self.send_otp()
        messagebox.showinfo("Info", "A new OTP has been sent!")

if __name__ == "__main__":
    window = OTPVerifier()
    window.labels()
    window.entry()
    window.buttons()
    window.mainloop()
