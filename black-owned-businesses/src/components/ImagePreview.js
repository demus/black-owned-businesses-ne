import React from "react";
import { string } from "prop-types";

// prettier-ignore
const businessTypeImagesMap = {
  "Bar": require("../images/bar.jpg"),
  "Catering": require("../images/catering.jpg"),
  "Cleaning Service": require("../images/cleaning.jpg"),
  "Coffee Shop": require("../images/coffee.jpg"),
  "Dairy Farm": require("../images/dairy.jpg"),
  "Farm": require("../images/farm.jpg"),
  "Food/Merchandise": require("../images/food.jpg"),
  "Gym/Fitness": require("../images/gym.jpg"),
  "Health/Beauty": require("../images/health.jpg"),
  "Hotel": require("../images/hotel.jpg"),
  "Marketing": require("../images/marketing.jpg"),
  "Photographer": require("../images/photographer.jpg"),
  "Restaurant": require("../images/restaurant.jpg"),
  "Retail": require("../images/retail.jpg"),
}

const ImagePreview = ({ businessType }) => {
  return (
    <img className="image-preview" src={businessTypeImagesMap[businessType]} />
  );
};

ImagePreview.propTypes = {
  businessType: string.isRequired,
};

export default ImagePreview;
