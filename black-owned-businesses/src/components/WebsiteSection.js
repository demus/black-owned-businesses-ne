import React from "react"; 
 import { string } from "prop-types";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faGlobe } from "@fortawesome/free-solid-svg-icons";

const removeProtocol = (website) => website.replace(/^\/\/|^.*?:\/\//, "");

const truncateUrl = (website, maxUrlLength=30, placeholder='...') => {
  website = removeProtocol(website);

  return website.length > maxUrlLength
    ? `${website.substring(
        0,
        maxUrlLength - placeholder.length
      )}${placeholder}`
    : website;
};

const WebsiteSection = ({ website }) => {
  return (
    <div className="website-section">
      <FontAwesomeIcon className="icon" icon={faGlobe} size="2x" />
      <a className="website-url" href={website}>
        {truncateUrl(website)}
      </a>
    </div>
  );
};

WebsiteSection.propTypes = {
  website: string.isRequired,
};

export default WebsiteSection;
