import { useState } from "react";
import { apiFetch, readApiResponse } from "../../api";
import Button from "../Layouts/Button";
import Input from "../Layouts/Input";
import ReturnButton from "../Layouts/ReturnButton";
import Link from "../Layouts/Link";

import AddFileButton from "../Layouts/AddFileButton";
import TextArea from "../Layouts/TextArea";
import AddImageButton from "../Layouts/AddImageButton";
import { useNavigate } from "react-router-dom";
import Text from "../Layouts/Text";
import Image from "../Layouts/Image";
import RemoveButton from "../Layouts/RemoveButton";
import PlayAudioButton from "../Layouts/PlayAudioButton";

import { useTranslation } from "react-i18next";
import VideoArea from "../Layouts/VideoArea";
import CustomLoadingButton from "../Layouts/CustumLoadingButton";

import useScreenOrientation from "react-hook-screen-orientation";
import Landscape from "./Landscape";

function AddItem() {
  const navigate = useNavigate();

  const [image, setImage] = useState(null);
  const [shownImage, setShownImage] = useState(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [audio, setAudio] = useState(null);
  const [audioName, setAudioName] = useState("");
  const [augmentedVideoOrImage, setAugmentedVideoOrImage] = useState("");
  const [extraVideo, setExtraVideo] = useState(null);
  const [shownVideo, setShownVideo] = useState("");
  const [pending, setPending] = useState(false);
  const [isImageBig, setIsImageBig] = useState(false);

  const [error, setError] = useState("");


  const { t } = useTranslation(["additem"]);
  const orientation = useScreenOrientation();

  const handleAddItem = async () => {
    if (title == "") {
      setError(t("You should fill title!"));
      // setMargin("58px");
      return;
    } else if (image == null) {
      setError(t("You should choose a target image!"));
      // setMargin("58px");
      return;
    } else {
      setPending(true);
      setError("");
      try {
      const currentItems = await readApiResponse(await apiFetch("/api/items/"));
      const nextIndex = currentItems.length;
      const data = new FormData();

      const new_image = new File([image], `${nextIndex}.jpg`);

      data.append("target_image", new_image);
      data.append("target_index", nextIndex);
      data.append("title", title);
      data.append("description", description);
      if (audio != null)
        data.append("audio", audio);
      else 
        data.append("audio", "")
      data.append("audio_name", audioName)
      data.append("augmented_video", augmentedVideoOrImage);
      if (extraVideo != null) {
        data.append("extra_video", extraVideo);
      } else {
        data.append("extra_video", "");
      }

      await readApiResponse(await apiFetch("/api/items/", {
        method: "POST",
        body: data,
      }));
      localStorage.setItem("stop", false);
      navigate("/dashboard");
      } catch (err) {
        setError(err.message || t("Unable to save artwork."));
      } finally {
        setPending(false);
      }
    }
  };

  const imageChange = (obj) => {
    if (obj != null && obj.size > 10 * 1024 * 1024) {
      setIsImageBig(true);
      return;
    }
    setIsImageBig(false);
    setImage(obj);
    if (obj != null) setShownImage(URL.createObjectURL(obj));
  };

  const videoChange = (obj) => {
    setExtraVideo(obj);
    if (obj != null) setShownVideo(URL.createObjectURL(obj));
  };

  const audioChange = (obj) => {
    setAudio(obj);
    setAudioName("");
    if (obj != null) setAudioName(obj.name)
  }

  return (
    <>
      {orientation == "landscape-primary" ||
      orientation == "landscape-secondary" ? (
        <Landscape />
      ) : (
        <>
          <ReturnButton />
          <div style={{ alignItems: "center", marginTop: "3%" }}>
            {image == null ? (
              <>
                <AddImageButton
                  width="70%"
                  marginLeft="15%"
                  text={t("add target image")}
                  stateChanger={imageChange}
                />
                {isImageBig ? (
                  <Link
                    text={t("Your image size must be less than 10 MB")}
                    color={"red"}
                  />
                ) : (
                  <Link text={t("Your image size must be less than 400KBs")} />
                )}
              </>
            ) : (
              <>
                <Image width="65%" left="16%" src={shownImage} />
                <RemoveButton stateChanger={imageChange} />
              </>
            )}

            <div style={{ marginTop: "3%" }}></div>

            <Input text={t("Title")} stateChanger={setTitle} />

            <div style={{ marginTop: "3%" }}></div>

            {audio == null ? (
              <AddFileButton text={t("add main audio")} accept="audio/*" stateChanger={audioChange} />
            ) : (
              <>
                <div style={{ marginTop: "3%" }}></div>
                <PlayAudioButton src={URL.createObjectURL(audio)} name={audioName} />
                <RemoveButton stateChanger={audioChange} />
              </>
            )}  
            

            <div style={{ marginTop: "1%" }}></div>

            <AddFileButton
              text={t("add augmented image or video")}
              accept="image/*,video/mp4,video/webm,video/quicktime"
              // class={"disabled"}
              stateChanger={setAugmentedVideoOrImage}
            />

            <div style={{ marginTop: "3%" }}></div>

            <TextArea text={t("Description")} stateChanger={setDescription} />

            <div style={{ marginTop: "1%" }}></div>

            {extraVideo == null ? (
              <AddFileButton
                text={t("add extra video")}
                accept="video/mp4,video/webm,video/quicktime,video/x-m4v"
                stateChanger={videoChange}
              />
            ) : (
              <>
                <div style={{ marginTop: "3%" }}></div>
                <VideoArea width="65%" left="16%" src={shownVideo} />
                <RemoveButton stateChanger={videoChange} />
              </>
            )}

            <div style={{ marginTop: "5%" }}></div>

            {error != "" && (
              <Text marginTop={"25px"} color={"red-text"} text={error} />
            )}
            <div style={{ marginTop: "10%" }}></div>

            {!pending && (
              <Button text={t("Done")} stateChanger={handleAddItem} />
            )}
            {pending && <CustomLoadingButton text={true} />}

            <div style={{ marginTop: "5%" }}></div>
          </div>
        </>
      )}
    </>
  );
}

export default AddItem;
