from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

def hash_password(password: str):
    """
        Generate a secure hash for a plain-text password.

        Uses the PBKDF2-SHA256 hashing algorithm to securely hash
        the provided password before storing it in the database.

        Args:
            password (str): The plain-text password to be hashed.

        Returns:
            str: The securely hashed password.
        """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """
        Verify a plain-text password against its hashed value.

        Compares the user-provided password with the stored hashed
        password and determines whether they match.

        Args:
            plain_password (str): The password entered by the user.
            hashed_password (str): The hashed password stored in
                the database.

        Returns:
            bool: True if the passwords match, otherwise False.
    """
    return pwd_context.verify(
        plain_password,
        hashed_password
    )