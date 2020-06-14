import json
from time import time


class FeatureCollection:
    def __init__(self):
        self.feature_collection = {"type": "FeatureCollection", "features": []}

    def add_point(self, latitude, longitude, properties):
        self.feature_collection["features"].append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                "properties": properties,
            }
        )

    @property
    def json(self):
        return json.dumps(self.feature_collection)

    def dump(self, filename):
        with open(f"{filename}-{time()}", "w") as features_json:
            json.dump(self.feature_collection, features_json)
