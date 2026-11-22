import Text from "./Text";
import Image from "./Image";
import "../../assets/CSS/itemCard.css";

function ItemCard(params) {
  const title = params.title.length > 13 ? `...${params.title.substring(0, 13)}` : params.title;
  return (
    <button type="button" className="card" onClick={params.onClick} aria-label={`Edit ${params.title}`}>
      <Image width="37%" height="90px" left="2%" src={params.image} />
      <div style={{ marginLeft: "40%", marginTop: "-75px" }}>
        <Text text={title} />
      </div>
    </button>
  );
}

export default ItemCard;
