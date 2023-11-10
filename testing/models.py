from pydantic import ValidationError, BaseModel
from datetime import datetime
from typing import Optional
from duffel_api.models import Offer


class DuffelAPIErrorData(BaseModel):
    departure_city: str
    destination_city: str
    departure_date: str
    cabin_class: str
    error_message: str


class DuffelAPIError(Exception):
    def __init__(self, error_data: DuffelAPIErrorData):
        self.error_data = error_data
        super().__init__(str(error_data))

    def __str__(self):
        return f"DuffelAPIError: {self.error_data.error_message} for trip from {self.error_data.departure_city} to {self.error_data.destination_city} on {self.error_data.departure_date}, cabin class: {self.error_data.cabin_class}"


class MyOffer(BaseModel):
    id: str
    total_amount: str
    airline_code: str
    airline_name: str
    num_segments: int
    departure_time: datetime
    arrival_time: datetime
    cabin_class: Optional[str] = None
    offer: Offer


class SuccessResponse(BaseModel):
    success: bool
    best_offer: MyOffer
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool
    best_offer: Optional[MyOffer] = None
    error: str
