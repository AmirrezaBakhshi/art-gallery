import { useState, useEffect } from "react";
import { apiFetch, readApiResponse } from "../../api";
import Input from "../Layouts/Input";
import "../../assets/CSS/button.css";

import TextArea from "../Layouts/TextArea";
import Button from "../Layouts/Button";
import AddImageButton from "../Layouts/AddImageButton";
import { useNavigate } from "react-router-dom";
import Text from "../Layouts/Text";
import ReturnButton from "../Layouts/ReturnButton";
import Image from "../Layouts/Image";

import { useTranslation } from "react-i18next";
import RemoveButton from "../Layouts/RemoveButton";

import useScreenOrientation from "react-hook-screen-orientation";
import Landscape from "./Landscape";

const toDataURL = (url) =>
  fetch(url)
    .then((response) => {
      if (!response.ok) throw new Error(`Image request failed (${response.status}).`);
      return response.blob();
    })
    .then((blob) => new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    }));

function dataURLtoFile(dataurl, filename) {
  const [header, encoded] = dataurl.split(",");
  const mime = header.match(/:(.*?);/)[1];
  const binary = atob(encoded);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return new File([bytes], filename, { type: mime });
}

function EditInfo() {
  const gallary = JSON.parse(localStorage.getItem("user"));

  const { t } = useTranslation(["gallaryinfo"]);
  const orientation = useScreenOrientation();

  const navigate = useNavigate();

  const [error, setError] = useState("");

  const [image, setImage] = useState(gallary.image);
  const [shownImage, setShownImage] = useState(gallary.image);
  const [name, setName] = useState(gallary.name);
  const [description, setDescription] = useState(gallary.description);
  const [contact, setContact] = useState(gallary.contact);
  const [address, setAddress] = useState(gallary.address);

  useEffect(() => {
    if (gallary.image != null) {
      toDataURL(gallary.image).then((dataUrl) => {
        setImage(dataURLtoFile(dataUrl, "imageName.jpg"));
      });
    }
  }, [gallary.image]);

  const handleEdit = async () => {
    const data = new FormData();
    data.append("name", name);
    data.append("username", gallary.username);
    data.append("email", gallary.email);

    if (image != null) {
      data.append("image", image);
    } else {
      data.append("image", "");
    }
    data.append("address", address);
    data.append("contact", contact);
    data.append("description", description);

    apiFetch(`/api/gallaries/${gallary.id}/`, {
      method: "PUT",
      body: data,
    })
      .then(readApiResponse)
      .then((data) => {
        localStorage.setItem("user", JSON.stringify(data));
        navigate("/dashboard");
      })
      .catch((err) => setError(err.message));
  };

  const imageChange = (obj) => {
    setImage(obj);
    if (obj != null) setShownImage(URL.createObjectURL(obj));
  };

  return (
    <>
      {orientation == "landscape-primary" ||
      orientation == "landscape-secondary" ? (
        <Landscape />
      ) : (
        <>
          <ReturnButton path={"/dashboard"} />
          <div style={{ marginTop: "30px" }} />
          {image == null ? (
            <AddImageButton
              shape="round"
              width="35%"
              marginLeft="32%"
              text={t("change or set profile image")}
              stateChanger={imageChange}
            />
          ) : (
            <>
              <Image
                shape="round"
                width="35%"
                height="125px"
                left="32%"
                src={shownImage}
              />
              <RemoveButton stateChanger={imageChange} />
            </>
          )}

          <div style={{ marginTop: "40px" }} />
          <Input
            text={t("Museum / Gallary name")}
            stateChanger={setName}
            initText={name}
          />
          <TextArea
            text={t("description")}
            stateChanger={setDescription}
            initText={description}
          />
          <Input
            type="number"
            text={t("phone/contact")}
            stateChanger={setContact}
            initText={contact}
          />
          <TextArea
            text={t("address")}
            stateChanger={setAddress}
            initText={address}
          />
          {error != "" && (
            <Text marginTop={"25px"} color={"red-text"} text={error} />
          )}
          <div style={{ marginTop: "40px" }} />
          <Button text={t("done")} stateChanger={handleEdit} />

          <div style={{ marginTop: "50px" }} />
        </>
      )}
    </>
  );
}

export default EditInfo;
