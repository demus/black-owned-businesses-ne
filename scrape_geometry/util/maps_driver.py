import json
import time

import usaddress
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class NoSearchResultError(Exception):
    pass


class NoAddressError(Exception):
    pass


class StateValidationError(Exception):
    pass


class MapsDriver:
    def __init__(self):
        self.driver = webdriver.Firefox()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.close()

    def place_details(self, title, city=None, state=None):
        text = " ".join([x for x in [title, city, state] if x is not None])
        tries = 3
        place_details_element = None
        for i in range(3):
            place_details_element = self.search(text)
            if place_details_element != None:
                break

        if place_details_element == None:
            raise TimeoutException()

        place_details_json = json.loads(
            place_details_element.get_attribute("data-entity")
        )
        entity_json = place_details_json.get("entity")

        # make sure that the entity is not a false positive
        if entity_json["address"] is None:
            raise NoAddressError()

        state_string = usaddress.tag(entity_json["address"])[0].get("StateName")
        if state and not states_match(state, state_string):
            raise StateValidationError()

        point_json = place_details_json.get("routablePoint")

        return {
            "business_title": entity_json.get("title"),
            "business_type": entity_json.get("primaryCategoryName"),
            "address": entity_json.get("address"),
            "phone": entity_json.get("phone"),
            "website": entity_json.get("website"),
            "menu_url": entity_json.get("menuUrl"),
            "latitude": point_json.get("latitude"),
            "longitude": point_json.get("longitude"),
        }

    def search(self, text):
        self.driver.get("https://www.bing.com/maps/")

        # prevents clicks on search bar while present
        search_bar_primer_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, "maps_sb_primer"))
        )
        WebDriverWait(self.driver, 20).until(EC.staleness_of(search_bar_primer_element))

        search_bar_element = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "maps_sb"))
        )
        search_bar_element.clear()
        search_bar_element.send_keys(text)
        search_bar_element.click()
        search_bar_element.send_keys(Keys.RETURN)

        place_details_element = None
        start_time = time.monotonic()

        while time.monotonic() - start_time < 20:
            # no search results
            try:
                WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "errmsg"))
                )
                raise NoSearchResultError(f"No matches found for {text}")
            except TimeoutException:
                pass

            # happy path: 1 search result
            try:
                place_details_element = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "overlay-taskpane"))
                )
                break
            except TimeoutException:
                pass

            # multiple search results
            # 'ul' is not always a direct child due to COVID banner
            try:
                place_details_element = WebDriverWait(self.driver, 1).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            ".entity-listing-container ul > li:nth-of-type(1) > a",
                        )
                    )
                )
                break
            except TimeoutException:
                pass

        return place_details_element


STATE_ABBREVIATIONS = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District Of Columbia",
    "FM": "Federated States Of Micronesia",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MH": "Marshall Islands",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "MP": "Northern Mariana Islands",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PW": "Palau",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VI": "Virgin Islands",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}

STATE_NAMES = {
    "Alabama": "AL",
    "Alaska": "AK",
    "American Samoa": "AS",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District Of Columbia": "DC",
    "Federated States Of Micronesia": "FM",
    "Florida": "FL",
    "Georgia": "GA",
    "Guam": "GU",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Marshall Islands": "MH",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Northern Mariana Islands": "MP",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Palau": "PW",
    "Pennsylvania": "PA",
    "Puerto Rico": "PR",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virgin Islands": "VI",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def states_match(state_abbr, text):
    if text is None:
        return False

    if len(text) == 2:
        return state_abbr == text

    return STATE_ABBREVIATIONS[state_abbr].lower() == text.strip().lower()
