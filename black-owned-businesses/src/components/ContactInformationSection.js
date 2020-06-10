import React from "react";
import { string } from "prop-types";

const ContactInformationSection = ({ businessTitle, address, phone }) => {
  return (
    <div>
      <div className="title">{businessTitle}</div>
      <div className="address">{address}</div>
      <div className="phone">{phone}</div>
    </div>
  );
};

ContactInformationSection.propTypes = {
  businessName: string.isRequired,
  address: string.isRequired,
  phone: string.isRequired,
};

export default ContactInformationSection;
