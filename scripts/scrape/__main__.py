import logging

import numpy as np
import pandas as pd
from selenium.common.exceptions import TimeoutException
from usaddress import RepeatedLabelError

from scrape.util.feature_collection import FeatureCollection
from scrape.util.maps_driver import (
    MapsDriver,
    NoAddressError,
    NoSearchResultError,
    StateValidationError,
)

logging.basicConfig()
logging.getLogger().setLevel(logging.ERROR)


if __name__ == "__main__":
    businesses_list_df = pd.read_csv(
        "./scrape/data/businesses_list.csv"
    )
    businesses_db_df = pd.read_csv(
        "./scrape/data/businesses_db.csv"
    )
    businesses_db_df = businesses_db_df.where(businesses_db_df.notnull(), None)

    business_types = set(np.concatenate([business_type.split('/') for business_type in businesses_list_df.business_type.unique()]))
    feature_collection = FeatureCollection()
    feature_collections = { business_type: FeatureCollection() for business_type in business_types }

    for index, row in businesses_db_df.iterrows():
        point_args = row.latitude, row.longitude, row.to_dict()
        feature_collection.add_point(*point_args)
        tags = row.business_type.split('/')
        [feature_collections[tag].add_point(*point_args) for tag in tags]


    with MapsDriver() as md:
        for index, row in businesses_list_df.iterrows():
            logging.debug(f"Row {index}: Started processing row")
            
            if (businesses_db_df.row_id == index).any():
                logging.debug(f"Row {index}: Skipping row. Row exists in DB.")
                continue

            try:
                place_details = md.place_details(
                    row.business_name, city=row.town, state=row.state
                )
            except (NoSearchResultError, NoAddressError, StateValidationError, RepeatedLabelError) as e:
                logging.error(f"Row {index}: Exception {type(e).__name__}")
                continue
            except TimeoutException:
                logging.error(f"Row {index}: Exception TimeoutException")
                continue

            logging.debug(f"Row {index}: Completed processing row successfully.")

            # the reference dataset defines a more granular business type than what can be scraped
            place_details["business_type"] = row.business_type

            if place_details["website"] is None:
                place_details["website"] = row.website

            place_details_row = pd.Series(
                [
                    index,
                    place_details['business_title'],
                    place_details['business_type'],
                    place_details['address'],
                    place_details['phone'],
                    place_details['website'],
                    place_details['menu_url'],
                    place_details['latitude'],
                    place_details['longitude'],
                ],
                index=['row_id', 'business_title', 'business_type', 'address', 'phone', 'website', 'menu_url', 'latitude', 'longitude']
            )
            businesses_db_df = businesses_db_df.append(place_details_row, ignore_index=True)

            # add to db df
            point_args = place_details["latitude"], place_details["longitude"], place_details
            feature_collection.add_point(*point_args)
            tags = place_details_row.business_type.split('/')
            [feature_collections[tag].add_point(*point_args) for tag in tags]
    

    feature_collection.dump("features.json")
    for k, v in feature_collections.items():
        v.dump(f"{k}.json")
    businesses_db_df.to_csv('./scrape/data/businesses_db.csv', index=False)

