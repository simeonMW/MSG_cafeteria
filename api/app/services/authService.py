from app.repositories.userRepo import UserRepo
from app.security import verify_pwd, hash_pwd, generate_token


class AuthService:
    """
    Logic for User Identity and Access Management (IAM).
    Implements Process 1.2 and coordinates with D1: Users.
    """

    @staticmethod
    def register_user(data):
        """
        Logic for Process 1.1 (Registration).
        Includes password hashing before data gets in the D1.
        """
        # email must be unique (Repo usually handles this, but Service provides the clear business error).
        if UserRepo.get_by_email(data.get('email')):
            return None, "A user with this email already exists."

        # hash password
        data['password'] = hash_pwd(data['password'])
        
        # New users are 'unverified' by default to satisfy Process 1.3
        user = UserRepo.create(data)
        return user, "Registration successful."

    @staticmethod
    def login_user(credentials):
        """
        Logic for Process 1.2 (Authentication).
        Enforces specialized identification rules based on the User Role.
        """
        email = credentials.get('email')
        password = credentials.get('password')
        emp_num = credentials.get('employee_number')

        user = UserRepo.get_by_email(email)

        # 1. Base Authentication Check
        if not user or not verify_pwd(password, user.password):
            return None, "Invalid email or password."

        # 2. Status Check (Process 1.3 Logic)
        # Prevent access if the HR manager has not verified the account.
        if not user.is_verified and user.role == 'customer':
            return None, "Account pending verification by HR Manager."

        # 3. Role-Specific Identification Check
        # certain roles must provide an Employee Number.
        if user.role in ['customer', 'hr_manager']:
            if not emp_num or user.employee_number != emp_num:
                return None, "Employee Number verification failed."

        # 4. Token
        # If all checks pass, generate the JWT for mobile/web app.
        token = generate_token(user.id, user.role)
        return {
            "token": token,
            "user": user.to_dict()
        }, "Login successful."


    @staticmethod
    def verify_account(user_id, admin_role):
        """
        Logic for Process 1.3 (Verification).
        Only allow the hr_manager to change the verification status.
        """
        if admin_role != 'hr_manager':
            return False, "Unauthorized: Only HR can verify accounts."
        
        user = UserRepo.update_verification_status(user_id, True)
        if user:
            return True, f"User {user.email} verified successfully."
        return False, "User not found."