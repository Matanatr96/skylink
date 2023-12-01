import os
import logging

import magicdate
from dotenv import load_dotenv
from duffel_api import Duffel
from typing import Optional, List
from models import MyOffer, DuffelAPIError, DuffelAPIErrorData, SuccessResponse, ErrorResponse
from datetime import datetime, time

load_dotenv(".env")
duffel = Duffel(access_token=os.getenv("DUFFEL_API_KEY"))
openai_api_key = os.getenv("OPENAI_API_KEY")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class DuffelManager:
    def __init__(self, api_client):
        self.api_client = api_client

    def call_duffel_api(self, departure_city: str, destination_city: str, departure_date: str,
                        cabin_class: str = None) -> str:
        logging.info("Calling Duffel API")
        slices = [{"origin": departure_city, "destination": destination_city, "departure_date": departure_date}]

        try:
            offer_request = self.api_client.offer_requests.create().slices(slices).passengers([{"type": "adult"}])
            if cabin_class:
                offer_request.cabin_class(cabin_class)
            offer_request_response = offer_request.execute()
            return offer_request_response.id
        except Exception as e:
            error_data = DuffelAPIErrorData(
                departure_city=departure_city,
                destination_city=destination_city,
                departure_date=departure_date,
                cabin_class=cabin_class or "Not Specified",
                error_message=str(e)
            )
            raise DuffelAPIError(error_data) from e

    @staticmethod
    def parse_offers(offers) -> list:
        return [
            MyOffer(
                id=raw_offer.id,
                total_amount=raw_offer.total_amount,
                airline_code=raw_offer.owner.iata_code,
                airline_name=raw_offer.owner.name,
                num_segments=len(raw_offer.slices[0].segments),
                departure_time=raw_offer.slices[0].segments[0].departing_at,
                arrival_time=raw_offer.slices[-1].segments[-1].arriving_at,
                cabin_class=raw_offer.slices[0].segments[0].passengers[0].cabin_class,
                offer=raw_offer,
            )
            for raw_offer in offers
        ]

    @staticmethod
    def calculate_offer_score(curr_offer, cost_weight, segments_weight, min_cost, max_segments):
        def normalize_value(value, min_value, max_value):
            if max_value - min_value == 0:
                return 0
            return (value - min_value) / (max_value - min_value)

        normalized_cost = normalize_value(float(curr_offer.total_amount), min_cost, min_cost)
        normalized_segments = normalize_value(curr_offer.num_segments, 0, max_segments)
        return (cost_weight * normalized_cost) + (segments_weight * normalized_segments)

    @staticmethod
    def is_time_of_day(departure_datetime: datetime, time_of_day: str) -> bool:
        # Define time ranges
        MORNING = (time(6, 0), time(12, 0))
        AFTERNOON = (time(12, 0), time(18, 0))
        EVENING = (time(18, 0), time(0, 0))
        NIGHT = (time(0, 0), time(6, 0))

        departure_time = departure_datetime.time()

        # Check the time of day
        if time_of_day.lower() == "morning":
            return MORNING[0] <= departure_time < MORNING[1]
        elif time_of_day.lower() == "afternoon":
            return AFTERNOON[0] <= departure_time < AFTERNOON[1]
        elif time_of_day.lower() == "evening":
            return EVENING[0] <= departure_time or departure_time < NIGHT[1]
        elif time_of_day.lower() == "night":
            return NIGHT[0] <= departure_time or departure_time < MORNING[0]
        else:
            message = "Invalid time_of_day value passed. Choose from 'morning', 'afternoon', 'evening', 'night'."
            logging.warning(message)
            raise ValueError(message)

    def get_best_offer(self, offers: List[MyOffer], airline_name: Optional[str] = None,
                       time_of_day: Optional[str] = None) -> Optional[MyOffer]:
        logging.info(f"Getting best offer from {len(offers)} offers")
        cost_weight = 0.7
        segments_weight = 0.3

        airline_filtered = []
        if airline_name:
            logging.info(f"Filtering for {airline_name} flights")
            airline_filtered = [offer for offer in offers if offer.airline_code.upper() == airline_name.upper()]
            logging.info(f"Num airlines after filtering {len(airline_filtered)}")
        filtered_offers = airline_filtered or offers

        tod_filtered = []
        if time_of_day:
            logging.info(f"Filtering for {time_of_day} flights")
            tod_filtered = [offer for offer in filtered_offers if
                            self.is_time_of_day(offer.departure_time, time_of_day)]
            logging.info(f"Num offers after filtering time of day: {len(tod_filtered)}")
        filtered_offers = tod_filtered or filtered_offers

        min_cost = min(float(offer.total_amount) for offer in filtered_offers)
        max_segments = max(offer.num_segments for offer in filtered_offers)

        return min(
            filtered_offers,
            key=lambda offer: self.calculate_offer_score(
                offer, cost_weight, segments_weight, min_cost, max_segments
            ),
        )

    def get_offer(self, departure_city: str, destination_city: str, departure_date: str, time_of_day: str = None,
                  airline_name: str = None, cabin_class: str = None):
        logging.info(
            f"Getting offer for departure_city: {departure_city}, destination_city: {destination_city}, departure_date: {departure_date}, time_of_day: {time_of_day}, airline: {airline_name}, cabin_class: {cabin_class}")
        try:
            offer_request_id = self.call_duffel_api(departure_city, destination_city, departure_date, cabin_class)
            offers_object = self.api_client.offers.list(offer_request_id, sort="total_amount")
            offers = self.parse_offers(offers_object)
            best_offer = self.get_best_offer(offers, airline_name=airline_name, time_of_day=time_of_day)
            logging.info("Returning best offer")
            return SuccessResponse(
                success=True,
                resp=best_offer,
            )

        except (ValueError, DuffelAPIError) as e:
            logging.error(f"{str(e)}")
            return ErrorResponse(
                success=False,
                error=str(e),
            )

    def test_get_one_offer(self, departure_city: str, destination_city: str, departure_date: str,
                           time_of_day: str = None, airline_name: str = None, cabin_class: str = None):
        # testing function to get one offer
        logging.info(
            f"Getting offer for departure_city: {departure_city}, destination_city: {destination_city}, departure_date: {departure_date}, time_of_day: {time_of_day}, airline: {airline_name}, cabin_class: {cabin_class}")
        offer_request_id = self.call_duffel_api(departure_city, destination_city, departure_date, cabin_class)
        return self.api_client.offers.list(offer_request_id, sort="total_amount")


def book_best_flight(departure_city: str, destination_city: str, departure_date: str, time_of_day: str = None,
                     airline_name: str = None, cabin_class: str = None):
    return DuffelManager(duffel).get_offer(departure_city, destination_city, departure_date, time_of_day, airline_name,
                                           cabin_class)


def get_absolute_date(relative_date: str):
    try:
        absolute_date = magicdate.magicdate(relative_date)
        string_date = datetime.strftime(absolute_date, "%Y-%m-%d")
        return SuccessResponse(
            success=True,
            resp=string_date
        )
    # improve this error handling
    except Exception:
        return ErrorResponse(
            success=False,
            error="Invalid date format. Try providing a relative date or an absolute date in the format YYYY-MM-DD",
        )

