import { useState } from "react";
import { apiFetch, readApiResponse } from "../../api";
import AddImageButton from "../Layouts/AddImageButton";
import Title from "../Layouts/Title";
import Input from "../Layouts/Input";
import "../../assets/CSS/button.css";
import "../../assets/CSS/artworkPreview.css";

import TextArea from "../Layouts/TextArea";
import Button from "../Layouts/Button";
import { useNavigate } from "react-router-dom";
import Image from "../Layouts/Image";
import RemoveButton from "../Layouts/RemoveButton";

import { useTranslation } from "react-i18next";

import useScreenOrientation from "react-hook-screen-orientation";
import Landscape from "./Landscape";

function AdditionalInfo() {
  const gallary = JSON.parse(localStorage.getItem("user")); //Fetches the user object from localStorage and parses it into a JavaScript object.

  const [image, setImage] = useState(null);
  const [shownImage, setShownImage] = useState(null);
  const [description, setDescription] = useState("");
  const [address, setAddress] = useState("");
  const [contact, setContact] = useState("");

  const { t } = useTranslation(["gallaryinfo"]);
  const orientation = useScreenOrientation();

  const navigate = useNavigate();  //edirecting the user to another page after form submission

  //This is an async function triggered when the user submits the form
  const handleSubmit = async () => { 
    const data = new FormData(); //Creates a new form data object to send data to a server.
    data.append("name", gallary.name); //Creates a new form data object to send data to a server.
    data.append("username", gallary.username);
    data.append("email", gallary.email);
    if (image != null) { //If an image has been selected (image is not null), it is added to the form data. Otherwise, an empty string is appended.
      data.append("image", image);
    } else {
      data.append("image", "");
    }
    data.append("address", address);
    data.append("contact", contact);
    data.append("description", description);

    apiFetch(`/api/gallaries/${gallary.id}/`, { //A fetch request is made to the server (PUT method to update an existing gallery).
      method: "PUT",
      body: data,
    })
      .then(readApiResponse)
      .then((data) => {
        localStorage.setItem("user", JSON.stringify(data));
        navigate("/dashboard");
      })
      .catch((err) => console.error(err));
  };

  const imageChange = (obj) => { //This function is called when the user selects an image
    setImage(obj); // obj: The selected image is passed in as a parameter. setImage: Updates the state with the selected image.
    if (obj != null) setShownImage(URL.createObjectURL(obj)); //If an image is selected (obj is not null), setShownImage creates a URL for the selected image and updates the shownImage state.
  };

  return (
    <>
      {orientation == "landscape-primary" ||
      orientation == "landscape-secondary" ? (
        <Landscape />
      ) : (
        <>
          <div style={{ marginTop: "50px" }} />
          <Title text={t("additional info")} />

          <div style={{ marginTop: "30px" }} />

          {image == null ? ( //Image handling: If image is null, the AddImageButton is shown to allow the user to upload an image. If an image is selected, it is displayed via the Image component.
            <AddImageButton
              shape="round"
              width="35%"
              marginLeft="32%"
              text={t("add image")}
              stateChanger={imageChange}
            />
          ) : (
            <>
              <div className="profile-image-preview">
                <Image
                  shape="round"
                  width="130px"
                  height="130px"
                  left="0"
                  src={shownImage}
                />
                <RemoveButton stateChanger={imageChange} />
              </div>
            </>
          )}

          <div style={{ marginTop: "30px" }} />
          <TextArea text={t("description")} stateChanger={setDescription} />
          <TextArea text={t("address")} stateChanger={setAddress} />
          <Input
            type={"number"}
            text={t("phone/contact")}
            stateChanger={setContact}
          />

          <div style={{ marginTop: "50px" }} />
          <Button text={t("next")} stateChanger={handleSubmit} /> 
          <div style={{ marginTop: "50px" }} />
        </>
      )}
    </>
  );
}

// A Button component with the text "next" triggers the handleSubmit function when clicked.
export default AdditionalInfo;
