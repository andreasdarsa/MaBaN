from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.enums import DatasetFormat
from app.services.upload_service import load_csv

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_200_OK,
)
def upload_dataset(
    file: UploadFile = File(...),
    dataset_format: DatasetFormat = Form(...),
    transaction_col: str = Form(...),
    item_col: str | None = Form(None),
):
    try:
        dataframe = load_csv(file)

        return {
            "filename": file.filename,
            "dataset_format": dataset_format,
            "transaction_col": transaction_col,
            "item_col": item_col,
            "rows": len(dataframe),
            "columns": dataframe.columns.tolist(),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    