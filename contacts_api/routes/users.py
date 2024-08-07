from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from contacts_api.database.db import get_db
from contacts_api.database.models import User
from contacts_api.repository import users as repository_users
from contacts_api.services.auth import auth_service
from contacts_api.conf.config import settings
from contacts_api.schemas import UserDB

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me/", response_model=UserDB, summary="Read Current User", description="Retrieve current user's details.")
async def read_users_me(
    current_user: User = Depends(auth_service.get_current_user)
) -> UserDB:
    """
    Retrieve current user's details.

    :param current_user: The current authenticated user.
    :type current_user: User
    :return: Current user's details.
    :rtype: UserDB
    """
    return current_user
    
  
@router.patch(
    "/avatar",
    response_model=UserDB,
    summary="Update User Avatar",
    description="Update current user's avatar image.",
)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
) -> UserDB:
    """
    Update current user's avatar image.

    :param file: The avatar image file to upload.
    :type file: UploadFile
    :param current_user: The current authenticated user.
    :type current_user: User
    :param db: The database session.
    :type db: Session
    :return: Updated user details.
    :rtype: UserDB
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    r = cloudinary.uploader.upload(
        file.file,
        public_id=f"ContactsApp/{current_user.username}",
        overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"ContactsApp/{current_user.username}").build_url(
        width=250, height=250, crop="fill", version=r.get("version")
    )

    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user