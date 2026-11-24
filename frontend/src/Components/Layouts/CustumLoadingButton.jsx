/* eslint-disable react/prop-types */
import "../../assets/CSS/button.css";
import Text from "./Text";

function CustomLoadingButton({ text }) {
  return (
    <>
      <button className="button loading-button" type="button" disabled aria-busy="true">
        <span className="loading-spinner" role="status" aria-label="Loading" />
      </button>
      {text && <Text text="this might take some time" />}
    </>
  );
}

export default CustomLoadingButton;
