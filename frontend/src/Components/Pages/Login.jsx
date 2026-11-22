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

function Login() {
  const navigate = useNavigate();
  const { t } = useTranslation(["login"]);
  const orientation = useScreenOrientation();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async () => {
    if (!username.trim() || !password) {
      setError(t("Please enter your username and password."));
      return;
    }

    setPending(true);
    setError("");
    try {
      const response = await apiFetch("/api/auth/login/", {
        method: "POST",
        body: JSON.stringify({ username: username.trim(), password }),
      });
      const payload = await readApiResponse(response);
      saveSession(payload);
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(err.message || t("Unable to log in."));
    } finally {
      setPending(false);
    }
  };

  return orientation === "landscape-primary" || orientation === "landscape-secondary" ? (
    <Landscape />
  ) : (
    <>
      <ReturnButton path="/" />
      <div style={{ alignItems: "center", marginTop: "180px" }}>
        <Input text={t("username")} stateChanger={setUsername} />
        <Input type="password" text={t("password")} stateChanger={setPassword} />
        {error && <Text marginTop="25px" color="red-text" text={error} />}
        <div style={{ marginTop: "50px" }} />
        {!pending ? (
          <Button text={t("login")} stateChanger={handleLogin} />
        ) : (
          <CustomLoadingButton />
        )}
        <Text marginTop="50px" text={t("don't have an account?")} />
        <Link text={t("click here to signup")} path="/signup" />
      </div>
    </>
  );
}

export default Login;
