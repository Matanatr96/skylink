# DuffelManager Class - README

## Overview
The `DuffelManager` class is a Python utility for interacting with the Duffel API to fetch, filter, and evaluate flight offers. It provides functionalities to make API calls, parse offers, calculate offer scores based on certain criteria, and fetch the best available offer based on user preferences.

## Requirements
- Python 3.x
- `duffel_api` library
- `dotenv` library for environment management
- `magicdate` library
- Custom models: `MyOffer`, `DuffelAPIError`, `DuffelAPIErrorData`, `SuccessResponse`, `ErrorResponse`
- Logging and datetime modules

## Setup
1. Install required libraries:
   ```bash
   pip install duffel_api python-dotenv magicdate
   ```
2. Create a `.env` file in the project root and add your Duffel API and OpenAI API keys:
   ```
   DUFFEL_API_KEY=your_duffel_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

### Initialization
Make your way to gpt-fc.ipynb and run the cells.
The function `user_interaction` will the your conversation with the flight booking agent

### Filtering Offers
The class provides functionality to filter offers based on airline, time of day, and cabin class.

### Additional Methods
- `call_duffel_api`: Internal method to call the Duffel API.
- `parse_offers`: Parses raw offers into a more usable format.
- `calculate_offer_score`: Calculates a score for each offer based on cost and segments.
- `is_time_of_day`: Checks if a departure time falls within a specified time of day.
- `get_best_offer`: Selects the best offer based on given criteria.
- `test_get_one_offer`: A testing method to fetch one offer.
- `book_best_flight`: Utility function to book the best flight based on given criteria.
- `get_absolute_date`: Converts a relative date to an absolute date.

## Error Handling
The class includes custom error handling, encapsulating errors within `DuffelAPIError` and providing meaningful error messages.

## Logging
Logging is configured to provide detailed information about the operations and errors during the execution of the class methods.

## Contributing
Contributions to enhance the `DuffelManager` class are welcome.
Please ensure to follow the existing coding style and add unit tests for any new or changed functionality.