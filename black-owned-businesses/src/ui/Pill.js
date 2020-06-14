import React from "react";

const Pill = ({ tag }) => {
  return (
    <span
      className={`pill ${tag
        .replace(" ", "-")
        .replace("/", "-")
        .toLowerCase()}`}
    >
      {tag}
    </span>
  );
};

export default Pill;
