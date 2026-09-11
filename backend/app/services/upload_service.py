from fastapi import UploadFile
import pandas as pd


def load_csv(file: UploadFile) -> pd.DataFrame:
    if not file.filename:
        raise ValueError("Uploaded file must have a filename.")

    try:
        dataframe = pd.read_csv(file.file)
    except Exception as exc:
        raise ValueError("Unable to read uploaded CSV file.") from exc

    if dataframe.empty:
        raise ValueError("Uploaded CSV file is empty.")

    return dataframe
