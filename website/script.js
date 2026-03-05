(() => {
  const burger = document.getElementById("burger");
  const mobileNav = document.getElementById("mobileNav");
  if (!burger || !mobileNav) return;

  const setOpen = (open) => {
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    mobileNav.hidden = !open;
  };

  burger.addEventListener("click", () => {
    const isOpen = burger.getAttribute("aria-expanded") === "true";
    setOpen(!isOpen);
  });

  // close after clicking a link
  mobileNav.querySelectorAll("a").forEach((a) => {
    a.addEventListener("click", () => setOpen(false));
  });
})();

