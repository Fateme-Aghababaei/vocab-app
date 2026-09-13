// Run before styles load to avoid flashing the wrong theme.
(() => {
  let preference;
  try {
    preference = localStorage.getItem("memento-theme");
  } catch {
    // System preference still works when storage is unavailable.
  }
  const dark = preference === "dark" ||
    (preference !== "light" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.documentElement.dataset.theme = dark ? "dark" : "light";
})();
