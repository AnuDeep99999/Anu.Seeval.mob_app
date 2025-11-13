from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
import random, re
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.template.loader import render_to_string


User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    data = request.data

    if 'otp' not in data:
        # Step 1: Receive signup data, generate OTP, save user as inactive with OTP
        email = data.get("email")
        password = data.get("password")
        phone = data.get("phone")
        country_code = data.get("country_code", "+91")  # default country code

        if not all([email, password, phone]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return Response({"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST)

        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
        if not re.match(password_regex, password):
            return Response({"error": "Password must be stronger."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(phone_number=phone).exists():
            return Response({"error": "Phone number already exists."}, status=status.HTTP_400_BAD_REQUEST)

        otp = str(random.randint(100000, 999999))
        otp_created_at = timezone.now()

        try:
            # Create user with inactive status, otp_code & otp_created_at saved
            user = User.objects.create_user(
                username=email,
                email=email,
                phone_number=phone,
                country_code=country_code,
                password=password,
                is_user=True,
                is_active=False,   # inactive until OTP verified
                otp_code=otp,
                otp_created_at=otp_created_at,
                is_verified=False
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Send OTP email
        try:
            send_mail(
                subject='Your OTP for Signup',
                message=f'Your OTP is {otp}. Valid for 10 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent to your email."})
        except Exception as e:
            # Cleanup user on mail send failure
            user.delete()
            return Response({"error": "Failed to send OTP email. " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        # Step 2: OTP verification
        user_otp = data.get("otp")
        email = data.get("email")

        if not all([user_otp, email]):
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({"error": "User already verified."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP expired (10 minutes)
        expiry_time = user.otp_created_at + timezone.timedelta(minutes=10)
        if timezone.now() > expiry_time:
            user.delete()  # delete user to force fresh signup if expired
            return Response({"error": "OTP expired. Please signup again."}, status=status.HTTP_400_BAD_REQUEST)

        if user_otp != user.otp_code:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP correct: activate user
        user.is_active = True
        user.is_verified = True
        user.otp_code = ""
        user.otp_created_at = None
        user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "User created successfully.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "email": user.email,
                "phone_number": user.phone_number,
                "country_code": user.country_code,
            }
        }, status=status.HTTP_201_CREATED)




@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    data = request.data
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return Response({"error": "Email and password required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    authenticated_user = authenticate(username=user.username, password=password)
    if authenticated_user:
        refresh = RefreshToken.for_user(authenticated_user)
        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "phone_number": user.phone_number,
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })
    else:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    reset_link = f"http://localhost:5173/reset-password?email={email}"  
    subject = 'Reset your password'
    message = render_to_string('reset_password_email.html', {
        'user': user,
        'reset_link': reset_link
    })

    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({"message": "Reset link sent."})


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    email = request.data.get('email')
    new_password = request.data.get('new_password')

    if not email or not new_password:
        return Response({"error": "Email and new password required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Password reset successfully."})


@api_view(["POST"])
def logout_view(request):
    request.user.last_logout = timezone.now()
    request.user.save()
    # For JWT logout, blacklist the token instead (if using token blacklist app)
    return Response({"message": "Logged out successfully."})



from rest_framework.permissions import IsAuthenticated

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    return Response({
        "id": user.id,
        "email": user.email,
        "name": user.get_full_name(),
        "phone_number": getattr(user, "phone_number", None),
        "country_code": getattr(user, "country_code", None),
    })
