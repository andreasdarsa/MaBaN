from typing import Optional
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from .models import PreprocessingResult, DatasetSummary

from .enums import DatasetFormat


def validate_dataset(
    df: pd.DataFrame,
    dataset_format: DatasetFormat | str,
    transaction_col: Optional[str] = None,
    item_col: Optional[str] = None,
    basket_item_cols: Optional[list[str]] = None,
    onehot_item_cols: Optional[list[str]] = None,
) -> DatasetFormat:
    try:
        dataset_format = DatasetFormat(dataset_format)
    except ValueError:
        supported = ", ".join(fmt.value for fmt in DatasetFormat)
        raise ValueError(
            f"Unsupported dataset format '{dataset_format}'. "
            f"Supported formats: {supported}."
        )

    if df.empty:
        raise ValueError("Dataset is empty.")

    if df.columns.duplicated().any():
        duplicated = df.columns[df.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names found: {duplicated}")

    columns = set(df.columns)

    if dataset_format == DatasetFormat.LONG:
        if not transaction_col:
            raise ValueError("transaction_col is required for long format.")

        if not item_col:
            raise ValueError("item_col is required for long format.")

        if transaction_col not in columns:
            raise ValueError(f"Column '{transaction_col}' does not exist.")

        if item_col not in columns:
            raise ValueError(f"Column '{item_col}' does not exist.")

        if transaction_col == item_col:
            raise ValueError(
                "transaction_col and item_col must be different."
            )

        if df[transaction_col].dropna().empty:
            raise ValueError(
                f"Column '{transaction_col}' is entirely empty."
            )

        if df[item_col].dropna().empty:
            raise ValueError(
                f"Column '{item_col}' is entirely empty."
            )

        if df[transaction_col].nunique(dropna=True) < 2:
            raise ValueError(
                "Dataset must contain at least two transactions."
            )

        if df[item_col].nunique(dropna=True) < 2:
            raise ValueError(
                "Dataset must contain at least two distinct items."
            )

    elif dataset_format == DatasetFormat.BASKET:
        if not basket_item_cols:
            raise ValueError(
                "basket_item_cols is required for basket format."
            )

        missing_cols = [
            col for col in basket_item_cols
            if col not in columns
        ]

        if missing_cols:
            raise ValueError(
                f"Basket item columns do not exist: {missing_cols}"
            )

        if len(basket_item_cols) < 2:
            raise ValueError(
                "Basket format requires at least two item columns."
            )

        if transaction_col is not None:
            if transaction_col not in columns:
                raise ValueError(
                    f"Column '{transaction_col}' does not exist."
                )

            if transaction_col in basket_item_cols:
                raise ValueError(
                    "transaction_col cannot also be an item column."
                )

        basket_values = df[basket_item_cols].stack().dropna()

        if basket_values.empty:
            raise ValueError(
                "Basket item columns are entirely empty."
            )

        if basket_values.nunique(dropna=True) < 2:
            raise ValueError(
                "Dataset must contain at least two distinct items."
            )

        if len(df) < 2:
            raise ValueError(
                "Dataset must contain at least two transactions."
            )

    elif dataset_format == DatasetFormat.ONEHOT:
        if not onehot_item_cols:
            raise ValueError(
                "onehot_item_cols is required for one-hot format."
            )

        missing_cols = [
            col for col in onehot_item_cols
            if col not in columns
        ]

        if missing_cols:
            raise ValueError(
                f"One-hot item columns do not exist: {missing_cols}"
            )

        if len(onehot_item_cols) < 2:
            raise ValueError(
                "One-hot format requires at least two item columns."
            )

        if transaction_col is not None:
            if transaction_col not in columns:
                raise ValueError(
                    f"Column '{transaction_col}' does not exist."
                )

            if transaction_col in onehot_item_cols:
                raise ValueError(
                    "transaction_col cannot also be an item column."
                )

        if len(df) < 2:
            raise ValueError(
                "Dataset must contain at least two transactions."
            )

        values = df[onehot_item_cols]
        allowed_values = {0, 1, True, False}

        invalid_mask = ~values.isin(allowed_values)

        if invalid_mask.any().any():
            raise ValueError(
                "One-hot item columns must contain only "
                "0/1 or True/False values."
            )

        if values.sum().sum() == 0:
            raise ValueError(
                "One-hot dataset contains no selected items."
            )

    return dataset_format


def clean_item_name(item: object) -> str:
    return str(item).strip().lower()


def long_to_transactions(
    df: pd.DataFrame,
    transaction_col: str,
    item_col: str,
) -> list[list[str]]:
    clean_df = df[[transaction_col, item_col]].dropna().copy()

    clean_df[item_col] = clean_df[item_col].apply(clean_item_name)
    clean_df = clean_df[clean_df[item_col] != ""]

    clean_df = clean_df.drop_duplicates(
        subset=[transaction_col, item_col]
    )

    return (
        clean_df
        .groupby(transaction_col)[item_col]
        .apply(list)
        .tolist()
    )


def basket_to_transactions(
    df: pd.DataFrame,
    basket_item_cols: list[str],
) -> list[list[str]]:
    transactions: list[list[str]] = []

    for _, row in df[basket_item_cols].iterrows():
        items: list[str] = []

        for item in row:
            if pd.isna(item):
                continue

            cleaned_item = clean_item_name(item)

            if cleaned_item:
                items.append(cleaned_item)

        # Αφαιρεί διπλότυπα διατηρώντας τη σειρά.
        items = list(dict.fromkeys(items))

        if items:
            transactions.append(items)

    return transactions


def encode_transactions(
    transactions: list[list[str]],
) -> pd.DataFrame:
    encoder = TransactionEncoder()
    encoded_array = encoder.fit(transactions).transform(transactions)

    return pd.DataFrame(
        encoded_array,
        columns=encoder.columns_,
    )


def onehot_to_encoded_df(
    df: pd.DataFrame,
    onehot_item_cols: list[str],
) -> pd.DataFrame:
    return df[onehot_item_cols].astype(bool).copy()


def summarize_transactions(
    transactions: list[list[str]],
) -> DatasetSummary:
    unique_items = {
        item
        for transaction in transactions
        for item in transaction
    }

    avg_basket_size = (
        sum(len(transaction) for transaction in transactions)
        / len(transactions)
        if transactions
        else 0.0
    )

    return DatasetSummary(
        num_transactions=len(transactions),
        num_unique_items=len(unique_items),
        avg_basket_size=float(avg_basket_size),
    )


def summarize_encoded_df(
    encoded_df: pd.DataFrame,
) -> DatasetSummary:
    basket_sizes = encoded_df.sum(axis=1)

    avg_basket_size = (
        float(basket_sizes.mean())
        if not encoded_df.empty
        else 0.0
    )

    return DatasetSummary(
        num_transactions=len(encoded_df),
        num_unique_items=encoded_df.shape[1],
        avg_basket_size=avg_basket_size,
    )


def preprocess_dataset(
    df: pd.DataFrame,
    dataset_format: DatasetFormat | str,
    transaction_col: Optional[str] = None,
    item_col: Optional[str] = None,
    basket_item_cols: Optional[list[str]] = None,
    onehot_item_cols: Optional[list[str]] = None,
) -> PreprocessingResult:
    validated_format = validate_dataset(
        df=df,
        dataset_format=dataset_format,
        transaction_col=transaction_col,
        item_col=item_col,
        basket_item_cols=basket_item_cols,
        onehot_item_cols=onehot_item_cols,
    )

    if validated_format == DatasetFormat.LONG:
        # Το validation εγγυάται ότι δεν είναι None.
        assert transaction_col is not None
        assert item_col is not None

        transactions = long_to_transactions(
            df=df,
            transaction_col=transaction_col,
            item_col=item_col,
        )

        encoded_df = encode_transactions(transactions)
        summary = summarize_transactions(transactions)

    elif validated_format == DatasetFormat.BASKET:
        assert basket_item_cols is not None

        transactions = basket_to_transactions(
            df=df,
            basket_item_cols=basket_item_cols,
        )

        encoded_df = encode_transactions(transactions)
        summary = summarize_transactions(transactions)

    elif validated_format == DatasetFormat.ONEHOT:
        assert onehot_item_cols is not None

        encoded_df = onehot_to_encoded_df(
            df=df,
            onehot_item_cols=onehot_item_cols,
        )

        transactions = None
        summary = summarize_encoded_df(encoded_df)

    else:
        # Αμυντικός έλεγχος για μελλοντική επέκταση του enum.
        raise RuntimeError(
            f"Dataset format '{validated_format}' has not been implemented."
        )

    return PreprocessingResult(
        dataset_format=validated_format,
        transactions=transactions,
        encoded_df=encoded_df,
        summary=summary,
    )
