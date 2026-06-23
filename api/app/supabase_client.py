import os
from supabase import create_client


def get_supabase_client():
    """Create and return a Supabase client from environment configuration."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set for Supabase storage operations."
        )

    return create_client(url, key)


class SupabaseStorage:
    """Helper wrapper for Supabase Storage bucket operations."""

    @staticmethod
    def bucket_name():
        return os.getenv("SUPABASE_STORAGE_BUCKET", "public")

    @staticmethod
    def upload_bytes(object_path: str, data: bytes, content_type: str):
        client = get_supabase_client()
        storage = client.storage()
        bucket = SupabaseStorage.bucket_name()

        response = storage.from_(bucket).upload(
            object_path,
            data,
            {
                "content-type": content_type,
            },
        )

        if response.get("error"):
            raise RuntimeError(
                f"Supabase upload failed: {response['error'].get('message', response['error'])}"
            )

        return object_path

    @staticmethod
    def create_signed_url(object_path: str, expires_in: int = 300):
        client = get_supabase_client()
        storage = client.storage()
        bucket = SupabaseStorage.bucket_name()

        signed_data = storage.from_(bucket).create_signed_url(object_path, expires_in)
        if isinstance(signed_data, dict) and signed_data.get("error"):
            raise RuntimeError(
                f"Supabase signed URL failed: {signed_data['error'].get('message', signed_data['error'])}"
            )

        if isinstance(signed_data, dict):
            return signed_data.get("signedUrl") or signed_data.get("signed_url")
        return signed_data

    @staticmethod
    def get_public_url(object_path: str):
        client = get_supabase_client()
        storage = client.storage()
        bucket = SupabaseStorage.bucket_name()

        public_data = storage.from_(bucket).get_public_url(object_path)
        if isinstance(public_data, dict):
            return public_data.get("publicUrl") or public_data.get("public_url")
        return public_data
