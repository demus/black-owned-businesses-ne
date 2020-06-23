import json
import time

import usaddress
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 30


class NoSearchResultError(Exception):
    pass


class NoAddressError(Exception):
    pass


class StateValidationError(Exception):
    pass


class BingMapsDriver:
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
        for i in range(tries):
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

        # sometimes element doesn't appear, possibly for slower connections
        try:
            # prevents clicks on search bar while present
            search_bar_primer_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "maps_sb_primer"))
            )
            WebDriverWait(self.driver, 10).until(
                EC.staleness_of(search_bar_primer_element)
            )
        except TimeoutException:
            pass

        search_bar_element = WebDriverWait(self.driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "maps_sb"))
        )
        search_bar_element.clear()
        search_bar_element.send_keys(text)
        # click is sometimes necessary for some reason
        search_bar_element.click()
        search_bar_element.send_keys(Keys.RETURN)

        place_details_element = None
        start_time = time.monotonic()

        while time.monotonic() - start_time < 20:
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

            # no search results, at end cause it usually isn't the case
            try:
                WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "errmsg"))
                )
                raise NoSearchResultError(f"No matches found for {text}")
            except TimeoutException:
                pass

        return place_details_element


class GoogleMapsDriver:
    def __init__(self):
        self.driver = webdriver.Firefox()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.driver.close()

    def _search_maps(self):
        self.driver.get("https://www.google.com/maps")

        search_box = WebDriverWait(self.driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.ID, "searchboxinput"))
        )
        search_box.clear()
        search_box.send_keys(self.query)
        # click is sometimes necessary for some reason
        search_box.click()
        search_box.send_keys(Keys.RETURN)

    @property
    def business_title(self):
        try:
            business_title_element = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "h1.section-hero-header-title-title span")
                )
            )
            return business_title_element.get_attribute("innerText")
        except TimeoutException:
            results = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "section-result"))
            )
            if len(results) > 1:
                # multiple results found
                return None
            else:
                # raise NoSearchResultError(f"No matches found for {self.query}")
                return None

    @property
    def business_type(self):
        business_type_element = self.driver.find_elements_by_css_selector(
            "span.section-rating-term button.widget-pane-link"
        )[-2]
        return business_type_element.get_attribute("innerText")

    @property
    def address(self):
        address_element = self.driver.find_elements_by_css_selector(
            "button[data-tooltip='Copy address']"
        )

        if not address_element:
            raise NoAddressError()

        return address_element[0].get_attribute("aria-label").split(":")[1].strip()

    @property
    def phone(self):
        phone_element = self.driver.find_elements_by_css_selector(
            "button[data-tooltip='Copy phone number']"
        )
        if not phone_element:
            return None
        return phone_element[0].get_attribute("aria-label").split(":")[1].strip()

    @property
    def website(self):
        website = ""
        try:
            website_element = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[data-tooltip='Open website']")
                )
            )
            website_element.click()
            # switch focus to newly opened tab and wait for the redirect to finish
            self.driver.switch_to.window(self.driver.window_handles[1])

            WebDriverWait(self.driver, TIMEOUT).until(
                lambda driver: (driver.current_url != "about:blank")
                & (not driver.current_url.startswith("https://www.google.com/"))
            )
            website = self.driver.current_url
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
        except TimeoutException:
            pass
        return website

    @property
    def menu_url(self):
        menu_url_element = self.driver.find_elements_by_css_selector(
            "button[data-tooltip='Open menu link']"
        )

        if not menu_url_element:
            return None

        menu_url_element[0].click()
        # switch focus to newly opened tab and wait for the redirect to finish
        self.driver.switch_to.window(self.driver.window_handles[1])
        WebDriverWait(self.driver, TIMEOUT).until(
            lambda driver: (driver.current_url != "about:blank")
            & (not driver.current_url.startswith("https://www.google.com/"))
        )
        menu_url = self.driver.current_url
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        # Remove google reference in URL
        return menu_url[:-11] if menu_url.endswith("?ref=google") else menu_url

    @property
    def location(self):
        return self.driver.current_url.split("@")[1].split(",")[:2]

    def place_details(self, title, city=None, state=None):
        self.query = " ".join([x for x in [title, city, state] if x is not None])
        self._search_maps()

        business_title = self.business_title
        if business_title is None:
            # raise NoSearchResultError(f"No matches found for {self.query}")
            return None

        latitude, longitude = self.location
        return {
            "business_title": business_title,
            "business_type": self.business_type,
            "address": self.address,
            "phone": self.phone,
            "website": self.website,
            "menu_url": self.menu_url,
            "latitude": latitude,
            "longitude": longitude,
        }


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
