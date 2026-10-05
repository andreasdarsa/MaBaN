from __future__ import annotations

import os
from typing import Any

import requests


class APIClientError(RuntimeError):
    """Raised when the MaBaN API returns an unexpected response."""


class MaBaNAPIClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = (
            base_url
            or os.getenv("MABAN_API_URL")
            or "http://localhost:8000/api/v1"
        ).rstrip("/")

        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            response = requests.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.exceptions.InvalidJSONError as exc:
            raise APIClientError(
                f"Could not encode request payload as JSON: {exc}"
            ) from exc

        except requests.RequestException as exc:
            raise APIClientError(
                f"Could not reach MaBaN API at {self.base_url}: "
                f"{type(exc).__name__}: {exc}"
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise APIClientError(
                "MaBaN API returned a non-JSON response "
                f"(HTTP {response.status_code})."
            ) from exc

        if not response.ok:
            detail = payload.get("detail", payload)

            raise APIClientError(
                f"API request failed ({response.status_code}): {detail}"
            )

        return payload

    def health(self) -> dict[str, Any]:
        return self._request(
            "GET",
            "/health",
        )

    def upload_dataset(
        self,
        file_bytes: bytes,
        filename: str,
        dataset_format: str,
        transaction_col: str,
        item_col: str | None = None,
    ) -> dict[str, Any]:

        files = {
            "file": (
                filename,
                file_bytes,
                "text/csv",
            ),
        }

        data = {
            "dataset_format": dataset_format,
            "transaction_col": transaction_col,
        }

        if item_col is not None:
            data["item_col"] = item_col

        return self._request(
            "POST",
            "/upload",
            files=files,
            data=data,
        )

    def run_analysis(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        return self._request(
            "POST",
            "/analysis",
            json=payload,
        )

    def recommend(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        return self._request(
            "POST",
            "/recommendations",
            json=payload,
        )


def get_api_client() -> MaBaNAPIClient:
    return MaBaNAPIClient()