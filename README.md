User Authentication System

The User Authentication System is a comprehensive software solution designed to provide secure and efficient user authentication mechanisms. It combines multiple approaches, including email verification, OTP-based authentication, and face recognition, to ensure robust user identity verification.


Features

1. Email Verification
- Sends a One-Time Password (OTP) to the user's email address.
- Allows the user up to three attempts to enter the correct OTP.
- Implements blocking of email addresses for 24 hours after multiple failed attempts.
- OTP expiration is set to 5 minutes for enhanced security.

2. OTP Verification
- Uses the Twilio API to send OTPs to users' mobile numbers.
- Provides GUI-based verification using Tkinter.
- Includes functionality to resend OTPs.

3. Face Authentication
- Leverages the DeepFace library for face recognition.
- Continuously verifies live camera feeds against a reference image.
- Displays real-time match results via OpenCV.


Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/user-authentication-system.git
   ```
2. Navigate to the project directory:
   ```bash
   cd user-authentication-system
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   The main libraries used are:
   - opencv-python
   - deepface
   - twilio
   - tkinter

4. Set up configuration:
   - Email verification requires valid email credentials and an SMTP server.
   - OTP-based verification requires Twilio credentials (SID, Auth Token, and a valid Twilio phone number).


Usage

Run Individual Modules

1. Email Verification:
   ```bash
   python Email_verification.py
   ```

2. OTP Verification:
   ```bash
   python OTPVerification.py
   ```

3. Face Authentication:
   ```bash
   python Face_Authentication.py
   ```

Run All-in-One System

To utilize all features together:
```bash
python All_in_one.py
```

Dependencies
- Python 3.x
- OpenCV
- DeepFace
- Twilio API
- Tkinter (pre-installed with Python)


Future Enhancements
- Add support for fingerprint-based authentication.
- Implement database integration for user data storage.
- Enhance GUI with modern frameworks like PyQt or Kivy.


License
This project is licensed under the MIT License. See the LICENSE file for more details.


Contributors
- Your Name - Developer Akarsh Chaturvedi
- Contributions are welcome! Feel free to submit a pull request.


Contact
For queries or support, contact:
- Email: your-Chaturvediakarsh51@gmail.com
- 
Screenshots

![Screenshot 2025-01-01 000409](https://github.com/user-attachments/assets/fa2b1d39-bf42-49b7-a52f-e09c2a779205)
