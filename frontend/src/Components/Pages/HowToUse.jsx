import Title from "../Layouts/Title";
import Text from "../Layouts/Text";
import ReturnButton from "../Layouts/ReturnButton";

export default function HowToUse() {
  return (
    <>
      <ReturnButton path="/" />
      <div style={{ marginTop: "45px" }} />
      <Title text="How to use ArtGallery" />
      <Text marginTop="30px" width="82%" text="For gallery teams: create an account, complete your gallery profile, then add artwork with a target image, title, description, and optional audio or video. Use the dashboard to edit your gallery profile and manage published items." />
      <Text marginTop="25px" width="82%" text="For visitors: open a collection item to view its image and description, play its audio guide or supporting video when available, and open the gallery profile for contact and location details." />
    </>
  );
}
