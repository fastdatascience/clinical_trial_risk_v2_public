import time
from datetime import datetime
from enum import Enum
from typing import Any
from decimal import Decimal

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import SQLModel


class ServerResponse(JSONResponse):
    def __init__(self, data: object = None, error: str | None = None, errors: list[str] | None = None, status_code: int = 200, headers: dict[str, str] | None = None) -> None:
        timestamp: int = int(time.time())
        self.data: Any = data
        self.error: str | None = error
        self.errors: list[str] | None = errors

        body = {"timestamp": timestamp, "data": self.serialize(self.data), "error": self.error, "errors": [self.error, *self.errors] if self.errors else None}

        super().__init__(content=body, status_code=status_code, headers=headers)

    def serialize(self, data: Any) -> Any:
        if isinstance(data, datetime):
            return data.isoformat()

        if isinstance(data, list):
            return [self.serialize(item) for item in data]

        if isinstance(data, dict):
            return {key: self.serialize(value) for key, value in data.items()}

        if isinstance(data, BaseModel | SQLModel):
            serialized_data = data.dict()
            for field_name, field_value in serialized_data.items():
                if field_value is None:
                    continue
                serialized_data[field_name] = self.serialize(field_value)
            return serialized_data

        if isinstance(data, Enum):
            return data.value

        if isinstance(data, Decimal):
            return float(data)

        return data
