from pydantic import BaseModel

class ImageResponse(BaseModel):
    id_image: str
    url: str

    class Config:
        from_attributes = True