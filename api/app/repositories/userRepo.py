from app.models.user import User, db

class UserRepo:
    """
    Data Access Layer for D1: Users.
    CRUD operations for the User entity.
    """

    @staticmethod
    def create(user_data):
        """
        Implementation of DFD 1.1 (Registration Process).
        Logs new user data to the D1 users data store.
        """
        new_user = User(
            email=user_data.get('email'),
            password=user_data.get('password'),
            employee_number=user_data.get('employee_number'),
            role=user_data.get('role'),
            is_verified=True #False must be default state until HR action
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @staticmethod
    def get_by_id(user_id):
        """Standard retrieval by Primary Key."""
        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email):
        """
        Used by Process 1.2 (Authentication).
        Retrieves user record for credential verification.
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all():
        """
        Requirement from DFD 1.2: 
        Allows HR to get a list of all customer users (verified and unverified).
        """
        return User.query.all()

    @staticmethod
    def update_verification_status(user_id, status):
        """
        Implementation of DFD 1.3 (Verification Process).
        Allows HR to update the 'is_verified' flag in D1.
        """
        user = User.query.get(user_id)
        if user:
            user.is_verified = status
            db.session.commit()
            return user
        return None

    @staticmethod
    def update_user(user_id, updated_data):
        """
        Implementation of DFD 1.4 (Maintain Process).
        Allows HR or the system to update existing user records.
        """
        user = User.query.get(user_id)
        if user:
            for key, value in updated_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            db.session.commit()
            return user
        return None

    @staticmethod
    def delete(user_id):
        """
        Administrative maintenance to remove users if necessary.
        Used with caution in auditable systems.
        """
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False