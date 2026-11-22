import { useNavigate } from "react-router-dom";
import "../../assets/CSS/title.css";

function ImageButton({ image, text, path }) {
  const navigate = useNavigate();

  return (
    <button
      type="button"
      onClick={() => path && navigate(path)}
      disabled={!path}
      aria-label={text}
      style={{
        display: "inline-flex",
        flexDirection: "column",
        alignItems: "center",
        gap: "8px",
        border: 0,
        background: "transparent",
        cursor: path ? "pointer" : "default",
        padding: "8px",
      }}
    >
      <img style={{ width: "85%" }} src={image} alt="" />
      <span className="title">{text}</span>
    </button>
  );
}

export default ImageButton;
