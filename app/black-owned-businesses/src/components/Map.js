import React, { useEffect } from "react";
import { renderToString } from "react-dom/server";

import L from "leaflet";

import PlaceDetailsPopup from "../components/PlaceDetailsPopup";
import features from "../features.json";

const Map = () => {
  useEffect(() => {
    const map = L.map("map").setView([42.3601, -71.0589], 12);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    L.geoJSON(features, {
      style: function (feature) {
        return { color: feature.properties.color };
      },
    })
      .bindPopup(
        (layer) => {
          return renderToString(
            <PlaceDetailsPopup placeDetails={layer.feature.properties} />
          );
        },
        { minWidth: 300 }
      )
      .addTo(map);
    map.locate({ setView: true });
  }, []);

  return <div id="map" />;
};

export default Map;
