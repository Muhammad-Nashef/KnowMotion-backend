import cloudinary
import cloudinary.uploader
from config import Config

cloudinary.config(
    cloud_name=Config.CLOUDINARY_CLOUD_NAME,
    api_key=Config.CLOUDINARY_API_KEY,
    api_secret=Config.CLOUDINARY_API_SECRET
)

def delete_image(public_id):
    print("Cloudinary config:", Config.CLOUDINARY_CLOUD_NAME, Config.CLOUDINARY_API_KEY, Config.CLOUDINARY_API_SECRET)

    """Delete image from Cloudinary"""
    if public_id:
        try:
            cloudinary.uploader.destroy(public_id)
            print("Cloudinary delete successful for public_id:", public_id)
            return True
        except Exception as e:
            print("Cloudinary delete failed:", e)
            return False
    return False