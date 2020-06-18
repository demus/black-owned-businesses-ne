import React from "react";
import { string } from "prop-types";

const ImagePreview = ({ businessType }) => {
  return (
    <img className="image-preview" src={businessType} />
  );
};

ImagePreview.propTypes = {
  businessType: string.isRequired,
};

export default ImagePreview;
