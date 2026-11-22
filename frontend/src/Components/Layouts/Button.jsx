import { useNavigate } from "react-router-dom";
import "../../assets/CSS/button.css";

function Button({ text, onClick, redirectPath, path, stateChanger, disabled = false }) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (disabled) return;
    if (onClick) {
      onClick();
      return;
    }
    if (redirectPath) {
      window.location.assign(redirectPath);
      return;
    }
    if (path) navigate(path);
    if (stateChanger) stateChanger();
  };

  return (
    <button className="button" type="button" onClick={handleClick} disabled={disabled}>
      {text}
    </button>
  );
}

export default Button;
