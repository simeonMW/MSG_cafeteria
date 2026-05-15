import uuid
import qrcode
import os
from io import BytesIO
from flask import current_app

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
        In a production environment, this could save to an S3 bucket or local storage.
        For this implementation, we define the logic for local filesystem persistence.
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
        
        # storage path (must exists in deployment)
        #directory = "app/static/qrcodes"
        directory = "static/qrcodes"
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        file_name = f"qr_{token_string[:8]}.png"
        file_path = os.path.join(directory, file_name)
        
        # Save image
        img.save(file_path)
        
        return file_path

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