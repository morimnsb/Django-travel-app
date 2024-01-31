import { useEffect } from "react";

export default function Logout() {
  useEffect(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("Userinfo");
    localStorage.removeItem("avatar");
    window.location.href = "/";
  });
}
