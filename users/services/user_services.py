from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.cache import cache
from common.errors import raise_validation_error

from users.services.otp_service import OTPService
from users.models.invites import Invitation

User = get_user_model()

class UserServices:
    """Service layer for user management"""

    @staticmethod
    def create_user(invitation=None, **validated_data):
        # Pop password and email to pass explicitly
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        role = validated_data.pop("role", User.Role.EMP)
        is_active = validated_data.pop("is_active", True)

        # Validate password before creating user
        temp_user = User(email=email, **validated_data)
        try:
            password_validation.validate_password(password, temp_user)
        except DjangoValidationError as e:
            raise_validation_error(e.messages, field="password")

        # Always create a normal user for invitation-based onboarding
        if role == User.Role.ADMIN:
            role = User.Role.EMP

        user = User.objects.create_customer(
            email=email,
            password=password,
            role=role,
            is_active=is_active,
            **validated_data
        )

        return user

    @staticmethod
    def create_user_with_invitation(key, **validated_data):
        try:
            invitation = Invitation.objects.get(key=key)
        except Invitation.DoesNotExist:
            raise_validation_error("Invalid invitation key.", field="key")

        if invitation.key_expired():
            raise_validation_error("This invitation has expired.", field="key")

        if invitation.accepted:
            raise_validation_error("This invitation has already been accepted.", field="key")

        validated_data["email"] = invitation.email
        validated_data["role"] = invitation.role

        user = UserServices.create_user(is_active=False, **validated_data)

        invitation.accepted = True
        invitation.save(update_fields=["accepted"])

        return user

    @staticmethod
    def get_user(user_id_or_email):
        if isinstance(user_id_or_email, int):
            return User.objects.get(id=user_id_or_email)
        return User.objects.get(email=user_id_or_email)
    @staticmethod
    def get_users_by_role(role_type):
        return User.objects.filter(role=role_type, is_deleted=False)

    @staticmethod
    def update_user(user, data):
        """
        Handles PATCH /users/
        """


        if "first_name" in data:
            user.first_name = data["first_name"]

        if "last_name" in data:
            user.last_name = data["last_name"]


        if "is_otp_required" in data:
            password = data.get("password")
            if not password:
                raise_validation_error("Password is required to change 2FA settings", field="password")
            if not user.check_password(password):
                raise_validation_error("Password is incorrect", field="password")
            user.is_otp_required = bool(data["is_otp_required"])


        if "new_password" in data:
            old_password = data.get("old_password")
            new_password = data.get("new_password")

            if not old_password:
                raise_validation_error("Old password is required", field="old_password")

            if not user.check_password(old_password):
                raise_validation_error("Old password is incorrect", field="old_password")

            if old_password == new_password:
                raise_validation_error("New password must be different from old password", field="new_password")

            try:
                password_validation.validate_password(new_password, user)
            except DjangoValidationError as e:
                raise_validation_error(e.messages, field="new_password")

            user.set_password(new_password)

        # 4️⃣ Change Email (OTP required)
        if "new_email" in data:
            new_email = data["new_email"].strip().lower()
            otp = data.get("otp")
            password = data.get("password")  # Require password

            # Validate new email isn't already taken
            if User.objects.filter(email=new_email).exclude(id=user.id).exists():
                raise_validation_error("Email already in use", field="new_email")

            # Before sending OTP, check password
            if not otp:
                if not password:
                    raise_validation_error("Password is required to change email", field="password")
                if not user.check_password(password):
                    raise_validation_error("Password is incorrect", field="password")

                # Send OTP to NEW email
                success, message = OTPService.send_otp(new_email, purpose="change_email", user=user)
                if not success:
                    raise_validation_error(message, field="new_email")

                cache.set(f"pending_email:{user.id}", new_email, 600)
                return None  # Signal to view that OTP was sent

            # Step 2: OTP provided → verify and update
            pending_email = cache.get(f"pending_email:{user.id}")
            if not pending_email:
                raise_validation_error("No pending email change request", field="new_email")
            if new_email != pending_email:
                raise_validation_error("Email does not match pending change request", field="new_email")

            success, message = OTPService.verify_otp(new_email, otp, purpose="change_email", user=user)
            if not success:
                raise_validation_error(message, field="otp")

            user.email = new_email
            user.is_email_verified = True
            cache.delete(f"pending_email:{user.id}")

        user.save()
        return user
