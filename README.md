# Secure Multi-Factor Authentication System

A comprehensive Python-based authentication system that implements multiple security layers and authentication methods using Tkinter for the GUI.

## Features

### Authentication Methods
- **Facial Recognition** with liveness detection
- **OTP Verification** via SMS, Email, WhatsApp, or Voice Call
- **Email Verification** with code, magic link, or one-click options
- **Voice Recognition** using speech patterns
- **QR Code Authentication** for mobile device integration
- **Behavioral Biometrics** analyzing typing patterns
- **Multi-Factor Authentication** combining multiple methods

### Security Features
- Four security levels: Low, Medium, High, Maximum
- Account locking after multiple failed attempts
- Comprehensive audit logging
- Encryption of sensitive data
- Session management with configurable timeout
- Security analytics dashboard
- Admin panel for user management

### Technical Implementation
- SQLite database for user credentials and logs
- bcrypt for password hashing
- Fernet encryption for sensitive data
- OpenCV and DeepFace for facial recognition
- QR code generation with qrcode library
- Twilio integration for OTP delivery (simulated)
- Matplotlib for security analytics visualization

## Installation

### Prerequisites
- Python 3.7+
- Tkinter (usually comes with Python)
- Required Python packages:

```bash
pip install bcrypt opencv-python deepface qrcode[pil] speechrecognition cryptography matplotlib scikit-learn pandas pillow
```

### Database Setup
The application automatically creates an SQLite database (`auth_system.db`) with the necessary tables on first run.

### Encryption Key
The system generates an encryption key (`encryption.key`) on first run to secure sensitive data.

## Usage

1. Run the application:
```bash
python auth_system.py
```

2. Select your desired security level (Low, Medium, High, Maximum)

3. Choose an authentication method:
   - Single method (Face, OTP, Email, Voice, QR)
   - Multi-Factor (combines multiple methods based on security level)

4. Follow the on-screen instructions for the selected authentication method

5. Upon successful authentication, access the secure dashboard

## Admin Features

The system includes an admin panel for:
- User registration and management
- System settings configuration
- Viewing security analytics
- Monitoring audit logs

## Security Considerations

- This is a demonstration system and should not be used in production without additional security measures
- Real implementations would require actual API integrations for:
  - SMS/Email delivery services (Twilio, AWS SES, etc.)
  - Voice recognition services
  - Facial recognition APIs
  - Secure storage solutions

## File Structure

```
auth_system.py      # Main application file
auth_system.db      # Database file (created automatically)
encryption.key      # Encryption key (created automatically)
```

## Customization

The system can be extended by:
- Adding new authentication methods
- Integrating with real APIs for communication services
- Enhancing the security analytics with real data
- Adding more user management features in the admin panel

## License

This project is for educational purposes. Please ensure compliance with relevant regulations when implementing authentication systems.


## Demo 
<img width="1919" height="998" alt="Screenshot 2025-09-19 192843" src="https://github.com/user-attachments/assets/e8da8eb4-6e73-4e99-a0de-898daf27e84d" />
<img width="1414" height="985" alt="Screenshot 2025-09-19 192857" src="https://github.com/user-attachments/assets/da10c763-8c24-4eb9-bf9a-5c2e05d575bf" />
<img width="1290" height="756" alt="Screenshot 2025-09-19 192906" src="https://github.com/user-attachments/assets/3a984488-cae1-44a6-a872-7e2ebb81535b" />
<img width="835" height="623" alt="Screenshot 2025-09-19 192921" src="https://github.com/user-attachments/assets/ea92c013-e2da-497a-812a-117f07e19fa0" />
<img width="1161" height="788" alt="Screenshot 2025-09-19 192937" src="https://github.com/user-attachments/assets/2f7fec0c-cedb-4b22-bfbd-15e3afe7ac88" />
<img width="1600" height="689" alt="Screenshot 2025-09-19 193010" src="https://github.com/user-attachments/assets/a33602c5-26e0-4c3d-9f97-461217b9cd64" />
<img width="991" height="649" alt="Screenshot 2025-09-19 193022" src="https://github.com/user-attachments/assets/d2cc9886-f822-448a-ab5c-f077cdb78520" />




