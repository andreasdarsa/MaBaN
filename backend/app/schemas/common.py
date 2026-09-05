from pydantic import BaseModel


class ExecutionMetadata(BaseModel):
    execution_time: float


class DatasetSummaryResponse(BaseModel):
    num_transactions: int
    num_unique_items: int
    avg_basket_size: float
