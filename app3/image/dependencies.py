from fastapi import HTTPException, status
from pydantic import UUID4

from .crud import read_image
from .models import Image


def valid_image_id(image_uid: UUID4) -> Image:
    item = read_image(uid=str(image_uid).replace("-", ""))
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image {image_uid} not found",
        )
    return item