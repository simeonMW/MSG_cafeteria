import uuid
import qrcode
import os
from io import BytesIO
from flask import current_app
from app.supabase_client import SupabaseStorage

class QRGen:
    """
    Utility class for Process 3.3.
    Handles the generation of unique identifiers and their visual QR representations.
    """

    @staticmethod
    def generate_secure_token():
        """
        Generates a universally unique identifier (UUID4).
        UUID4 is used to ensure randomness and prevent sequential token guessing.
        """
        return str(uuid.uuid4())

    @staticmethod
    def create_qr_image(token_string):
        """
        Generates a QR code image from the provided token.
        saves to a bucket, In a production environment
        """
        # QR instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(token_string)
        qr.make(fit=True)

        # QR image 
        img = qr.make_image(fill_color="black", back_color="white")

        # Upload the generated image to Supabase Storage bucket.
        file_name = f"qrcodes/qr_{token_string[:8]}.png"
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return SupabaseStorage.upload_bytes(file_name, buffer.getvalue(), "image/png")

    @staticmethod
    def get_qr_bytes(token_string):
        """
        Helper method to return the QR code as a byte stream.
        Useful for serving the image directly to the Mobile App without saving to disk.
        """
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(token_string)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buf = BytesIO()
        img.save(buf)
        buf.seek(0)
        return buf.getvalue()