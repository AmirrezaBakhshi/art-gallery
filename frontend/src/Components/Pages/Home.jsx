import Logo from "../Layouts/Logo";
import Button from "../Layouts/Button";
import Text from "../Layouts/Text";
import Link from "../Layouts/Link";
import ImageButton from "../Layouts/ImageButton";
import about_us_img from "../../assets/Media/about-us.png";
import how_to_img from "../../assets/Media/how-to.png";

import { useTranslation } from "react-i18next";
import useScreenOrientation from "react-hook-screen-orientation";

import ReturnButton from "../Layouts/ReturnButton";
import Landscape from "./Landscape";

function Home() {
  const { t } = useTranslation(["home"]);
  const orientation = useScreenOrientation();

  return (
    <>
      {orientation == "landscape-primary" ||
      orientation == "landscape-secondary" ? (
        <Landscape />
      ) : (
        <>
          <ReturnButton notHasReturn={true} />
          <div style={{ alignItems: "center" }}>
            <Logo width={100} />
            {import.meta.env.VITE_SCANNER_URL ? (
              <Button text={t("scan")} redirectPath={import.meta.env.VITE_SCANNER_URL} />
            ) : null}
            <Text
              marginTop={"50px"}
              text={t("Do you own a museum / gallary?")}
            />
            <Link text={t("Click here to signup")} path="/signup" />
          </div>

          <div
            style={{
              marginTop: "120px",
              justifyContent: "space-around",
              display: "flex",
            }}
          >
            <ImageButton
              image={about_us_img}
              text={t("About Us")}
              path="/aboutus"
            />
            <ImageButton image={how_to_img} text={t("How to Use")} path="/how-to-use" />
          </div>
          <div style={{ marginTop: "50px" }}></div>
        </>
      )}
    </>
  );
}

export default Home;
