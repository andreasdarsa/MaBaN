from pydantic import BaseModel

from app.core.enums import DatasetFormat


class UploadConfig(BaseModel):
    dataset_format: DatasetFormat
    transaction_col: str
    item_col: str | None = None
    