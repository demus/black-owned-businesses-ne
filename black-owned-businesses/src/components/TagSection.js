import React from "react";
import { string } from "prop-types";

import Pill from "../ui/Pill";

const TagSection = ({ businessType }) => {
  return (
    <div className="tags">
      {[businessType, "Black-Owned"].map((tag) => (
        <Pill id={tag} tag={tag} />
      ))}
    </div>
  );
};

TagSection.propTypes = {
  businessType: string.isRequired,
};

export default TagSection;
