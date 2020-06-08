import pytest

from scrape_geometry.util.maps_driver import (
    MapsDriver,
    NoAddressError,
    NoSearchResultError,
)


def test_no_search_results():
    with MapsDriver() as md, pytest.raises(NoSearchResultError):
        md.place_details("asdfghjkl")


def test_invalid_address_error():
    with MapsDriver() as md, pytest.raises(NoAddressError):
        md.place_details("Boston MA")


def test_one_search_result():
    with MapsDriver() as md:
        md.place_details("345 Harrison Ave", city="Boston", state="MA")


def test_multiple_search_results():
    # multiple search results
    with MapsDriver() as md:
        md.place_details("dunkin")


def test_multiple_search_results_with_covid_warning():
    with MapsDriver() as md:
        md.place_details("Everybody Fights Boxing Gym Boston MA")
