import { useState, useEffect } from "react";
import { apiFetch, readApiResponse } from "../../api";
import ReturnButton from "../Layouts/ReturnButton";
import ItemCard from "../Layouts/ItemCard";

import useScreenOrientation from "react-hook-screen-orientation";
import Landscape from "./Landscape";
import Link from "../Layouts/Link";

import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

function Library() {
  const orientation = useScreenOrientation();

  const gallary = JSON.parse(localStorage.getItem("user"));
  const navigate = useNavigate();

  const [itemsList, setItemsList] = useState([]);

  const { t } = useTranslation(["iteminfo"]);

  useEffect(() => {
    apiFetch("/api/items/")
      .then(readApiResponse)
      .then((data) => setItemsList(data.filter((item) => item.gallary_id === gallary.id)))
      .catch((err) => console.error(err));
  }, [gallary.id]);

  return (
    <>
      {orientation == "landscape-primary" ||
      orientation == "landscape-secondary" ? (
        <Landscape />
      ) : (
        <>
          <ReturnButton path="/dashboard" />
          {itemsList.length > 0 ? (
            <div>
              {itemsList.map((item) => (
                <ItemCard
                  key={item.id}
                  image={item.target_image}
                  title={item.title}
                  onClick={() => {
                    localStorage.setItem("item", JSON.stringify(item));
                    navigate("/editItem")
                  }}
                />
              ))}
            </div>
          ) : (
            <div>
              <Link marginTop="50%" text={t("there is no item")} />
              <Link marginTop="5%" text={t("in the library right now!")} />
            </div>
          )}
        </>
      )}
    </>
  );
}

export default Library;
