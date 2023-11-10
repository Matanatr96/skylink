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

    def __str__(self):
        return f"This flight is on {self.airline_name} with {self.num_segments - 1} stops on {self.departure_time} in {self.cabin_class} class for ${self.total_amount}"


class SuccessResponse(BaseModel):
    success: bool
    resp: object
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool
    resp: Optional[object] = None
    error: str
