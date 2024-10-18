# authentication/views.py
import random
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from twilio.rest import Client
from django.conf import settings
from .models import PhoneOTP
from .serializers import OTPRequestSerializer, OTPVerifySerializer

# Send OTP using Twilio
def send_otp(phone_number):
    otp = random.randint(100000, 999999)  # Generate a random 6-digit OTP
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=f'Your OTP is {otp}',
        from_=settings.TWILIO_PHONE_NUMBER,
        to=phone_number
    )
    return otp

# Request OTP API
@api_view(['POST'])
def request_otp(request):
    serializer = OTPRequestSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        otp = send_otp(phone_number)
        
        # Save OTP to the database
        PhoneOTP.objects.update_or_create(
            phone_number=phone_number, 
            defaults={'otp': otp, 'validated': False}
        )
        
        return Response({'status': 'OTP sent'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Verify OTP API
@api_view(['POST'])
def verify_otp(request):
    serializer = OTPVerifySerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        otp = serializer.validated_data['otp']
        
        # Check if OTP exists in the database
        otp_entry = PhoneOTP.objects.filter(phone_number=phone_number, otp=otp).first()
        if otp_entry:
            otp_entry.validated = True
            otp_entry.save()
            return Response({'status': 'OTP verified'}, status=status.HTTP_200_OK)
        return Response({'status': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
