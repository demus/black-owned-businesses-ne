import React from "react";
import { shape } from "prop-types";

import ImagePreview from "../components/ImagePreview";
import TagSection from "../components/TagSection";
import WebsiteSection from "../components/WebsiteSection";
import MenuSection from "../components/MenuSection";
import ContactInformationSection from "./ContactInformationSection";

const PlaceDetailsPopup = ({ placeDetails }) => {
  const {
    business_title: businessTitle,
    business_type: businessType,
    address,
    phone,
    website,
    menu_url: menuURL,
  } = placeDetails;

  return (
    <div className="popup">
      <ImagePreview businessType={businessType} />
      <div className="sections">
        <ContactInformationSection
          businessTitle={businessTitle}
          address={address}
          phone={phone}
        />
        <TagSection businessType={businessType} />
        <WebsiteSection website={website} />
        {menuURL && <MenuSection menuURL={menuURL} />}
      </div>
    </div>
  );
};

PlaceDetailsPopup.propTypes = {
  placeDetails: shape().isRequired,
};

export default PlaceDetailsPopup;
