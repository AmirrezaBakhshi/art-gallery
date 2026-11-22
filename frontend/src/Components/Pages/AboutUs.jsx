import Title from "../Layouts/Title";
import Text from "../Layouts/Text";
import ReturnButton from "../Layouts/ReturnButton";

export default function AboutUs() {
  return (
    <>
      <ReturnButton path="/" />
      <div style={{ marginTop: "45px" }} />
      <Title text="About ArtGallery" />
      <Text
        marginTop="35px"
        width="82%"
        text="ArtGallery is a digital platform for galleries and museums to present their collections. Gallery teams can publish artwork images, descriptions, audio guides, and supporting videos, while visitors can browse public collection items and gallery profiles."
      />
    </>
  );
}
