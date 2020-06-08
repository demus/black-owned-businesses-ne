import logging

import pandas as pd
from selenium.common.exceptions import TimeoutException

from scrape_geometry.util.feature_collection import FeatureCollection
from scrape_geometry.util.maps_driver import (
    MapsDriver,
    NoAddressError,
    NoSearchResultError,
    StateValidationError,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":
    businesses_df = pd.read_csv(
        "./scrape_geometry/data/new_england_black_owned_businesses.csv"
    )
    feature_collection = FeatureCollection()

    with MapsDriver() as md:
        for index, row in businesses_df.iterrows():
            logging.info(f"Processing row at index {index}")

            try:
                place_details = md.place_details(
                    row.business_name, city=row.town, state=row.state
                )
            except (NoSearchResultError, NoAddressError, StateValidationError) as e:
                logging.error(f"{type(e).__name__} at index {index}")
                continue
            except TimeoutException:
                logging.error(f"TimeoutException at index {index}")
                continue

            logging.info(place_details)

            if place_details["business_type"] is None:
                place_details["business_type"] = row.business_type

            if place_details["website"] is None:
                place_details["website"] = row.website_or_social_from_csv

            place_details["city"] = row.town
            place_details["state_abbr"] = row.state

            feature_collection.add_point(
                place_details["latitude"], place_details["longitude"], place_details
            )

    logging.info(feature_collection.json)
    feature_collection.dump("features")
