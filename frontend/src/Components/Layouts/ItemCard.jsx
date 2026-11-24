import "../../assets/CSS/itemCard.css";

function ItemCard(params) {
  return (
    <button
      type="button"
      className="card"
      onClick={params.onClick}
      aria-label={`Edit ${params.title}`}
    >
      <img className="item-card-image" src={params.image} alt="" />
      <span className="item-card-title">{params.title}</span>
    </button>
  );
}

export default ItemCard;
