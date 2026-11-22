import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import useScreenOrientation from "react-hook-screen-orientation";

import Button from "../Layouts/Button";
import Input from "../Layouts/Input";
import Text from "../Layouts/Text";
import ReturnButton from "../Layouts/ReturnButton";
import Link from "../Layouts/Link";
import CustomLoadingButton from "../Layouts/CustumLoadingButton";
import Landscape from "./Landscape";
import { apiFetch, readApiResponse, saveSession } from "../../api";

function Signup() {
  const navigate = useNavigate();
  const { t } = useTranslation(["gallaryinfo"]);
  const orientation = useScreenOrientation();
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  const handleSubmit = async () => {
    if (![name, username, email, password].every((value) => value.trim())) {
      setError(t("You should fill all fields!"));
      return;
    }
    setPending(true);
    setError("");
    try {
      const response = await apiFetch("/api/gallaries/", {
        method: "POST",
        body: JSON.stringify({ name: name.trim(), username: username.trim(), email: email.trim(), password }),
      });
      const payload = await readApiResponse(response);
      saveSession(payload);
      navigate("/additionalinfo", { replace: true });
    } catch (err) {
      setError(err.message || t("Unable to create the gallery account."));
    } finally {
      setPending(false);
    }
  };

  return orientation === "landscape-primary" || orientation === "landscape-secondary" ? (
    <Landscape />
  ) : (
    <>
      <ReturnButton path="/" />
      <div style={{ alignItems: "center", marginTop: "60px" }}>
        <Input text={t("Museum / Gallary name")} stateChanger={setName} />
        <Input text={t("username")} stateChanger={setUsername} />
        <Input text={t("email")} stateChanger={setEmail} />
        <Input type="password" text={t("password")} stateChanger={setPassword} />
        {error && <Text marginTop="25px" color="red-text" text={error} />}
        <div style={{ marginTop: "40px" }} />
        {!pending ? (
          <Button text={t("signup")} stateChanger={handleSubmit} />
        ) : (
          <CustomLoadingButton />
        )}
        <Text marginTop="40px" text={t("Already have an account?")} />
        <Link text={t("Click here to login")} path="/login" />
        <div style={{ marginTop: "60px" }} />
      </div>
    </>
  );
}

export default Signup;
