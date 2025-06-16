from pydantic import BaseModel

#Xác thực OTP
class OTPVerifyRequest(BaseModel):
    email: str
    otp: str

class OTPResendRequest(BaseModel):
    email: str

class ForgotPasswordRequest(BaseModel):
    email: str
    
class PasswordResetRequest(BaseModel):
    email: str
    otp: str
    new_password: str
    
class PasswordChangeRequest(BaseModel):
    token: str
    old_password: str
    new_password: str