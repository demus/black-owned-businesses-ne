import React from "react";
import { string } from "prop-types";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faUtensils } from "@fortawesome/free-solid-svg-icons";

const MenuSection = ({ menuURL }) => {
  return (
    <div className="menu-section">
      <FontAwesomeIcon className="icon" icon={faUtensils} size="2x" />
      <a className="menu-url" href={menuURL}>
        Menu
      </a>
    </div>
  );
};

MenuSection.propTypes = {
  menuURL: string.isRequired,
};

export default MenuSection;
