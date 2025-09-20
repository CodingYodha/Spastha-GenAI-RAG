import requests
from django.conf import settings
from ninja import NinjaAPI
from .schema import LoginSchema, SignupSchema, TokenSchema
from django.contrib.auth import authenticate
from .models import SpashtUser
from rest_framework_simplejwt.tokens import RefreshToken
from ninja.errors import ValidationError
from rest_framework_simplejwt.views import TokenRefreshView
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
import google.auth.transport.requests
from google.auth import impersonated_credentials
from google.auth import jwt 

api = NinjaAPI(title="Spasht API Docs")

@api.get("/get-gcp-token")
def get_gcp_token(request):
    user = request.user
    if not user.is_authenticated:
        return api.create_response(request, {"error": "Unauthorized"}, status=401)
    target_scopes = ["https://www.googleapis.com/auth/devstorage.read_write"]
    request_adapter = google.auth.transport.requests.Request()
    wif_credentials = jwt.Credentials.from_signing_credentials(
        signing_credentials=settings.GCP_SIGNING_CREDENTIALS,
        issuer=settings.GCP_ISSUER,
        subject=user.username,
        audience=settings.GCP_AUDIENCE,
    )
    impersonated_creds = impersonated_credentials.Credentials(
        source_credentials=wif_credentials,
        target_principal=settings.GCP_SERVICE_ACCOUNT,
        target_scopes=target_scopes,
        lifetime=900, 
    )
    access_token = impersonated_creds.token
    impersonated_creds.refresh(request_adapter)
    return {"access_token": impersonated_creds.token}

def verify_recaptcha(token: str) -> bool:
    url = "https://www.google.com/recaptcha/api/siteverify"
    payload = {"secret": settings.RECAPTCHA_SECRET_KEY, "response": token}
    r = requests.post(url, data=payload)
    result = r.json()
    return result.get("success", False) and result.get("score", 0.5) >= 0.5

def send_verification_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    verify_url = f"{settings.FRONTEND_URL}/verify-email/{uid}/{token}"

    send_mail(
        "Verify your email",
        f"Hi {user.username},\n\nPlease verify your email by clicking this link:\n{verify_url}\n\nThank you!",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )


@api.post("/signup")
def signup(request, data: SignupSchema):
    if not verify_recaptcha(data.recaptcha_token):
        return api.create_response(request, {"error": "reCAPTCHA failed"}, status=400)

    if SpashtUser.objects.filter(username=data.username).exists():
        raise ValidationError([{"loc": ["username"], "msg": "Username already exists"}])
    if SpashtUser.objects.filter(email=data.email).exists():
        raise ValidationError([{"loc": ["email"], "msg": "Email already exists"}])

    if data.password1 != data.password2:
        return api.create_response(request, {"error": "Passwords don't match"}, status=400)

    user = SpashtUser.objects.create_user(
        username=data.username,
        email=data.email,
        password=data.password1,
        place=data.place,
        date_of_birth=data.date_of_birth,
        profession=data.profession,
        mobile_no=data.mobile_no,
        is_active=False
    )
    user.save()

    send_verification_email(user)

    return {"message": "User registered. Please check your email to verify your account."}


@api.get("/verify-email/{uidb64}/{token}")
def verify_email(request, uidb64: str, token: str):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = SpashtUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, SpashtUser.DoesNotExist):
        return api.create_response(request, {"error": "Invalid link"}, status=400)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return {"message": "Email verified successfully!"}
    else:
        return api.create_response(request, {"error": "Invalid or expired token"}, status=400)


@api.post("/refresh")
def refresh(request):
    view = TokenRefreshView.as_view()
    return view(request._request)


@api.post("/login", response=TokenSchema)
def login(request, data: LoginSchema):
    if not verify_recaptcha(data.recaptcha_token):
        return api.create_response(request, {"error": "reCAPTCHA failed"}, status=400)

    user = authenticate(username=data.username, password=data.password)
    if user is None:
        return api.create_response(request, {"error": "Invalid credentials"}, status=401)

    if not user.is_active:
        return api.create_response(request, {"error": "Please verify your email first"}, status=403)

    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}
