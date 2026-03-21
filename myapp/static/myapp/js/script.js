(function () {

  const slides = document.querySelectorAll(".hero-slide");
  const dots = document.querySelectorAll(".hero-slider-dots .dot");

  let current = 0;
  const total = Math.min(slides.length, dots.length);
  const intervalMs = 3500;

  let timer = null;

  if (total > 0) {

    function setSlide(index) {
      if (index < 0 || index >= total) return;

      slides.forEach(s => s.classList.remove("active"));
      dots.forEach(d => d.classList.remove("active"));

      if (slides[index] && dots[index]) {
        slides[index].classList.add("active");
        dots[index].classList.add("active");
        current = index;
      }
    }

    function nextSlide() {
      let next = current + 1;
      if (next >= total) next = 0;
      setSlide(next);
    }

    function startSlider() {
      if (timer) clearInterval(timer);
      timer = setInterval(nextSlide, intervalMs);
    }

    dots.forEach((dot, i) => {
      dot.addEventListener("click", () => {
        setSlide(i);
        startSlider();
      });
    });

    setSlide(0);
    startSlider();
  }

})();

const hamburger = document.getElementById("hamburger");
const navCenter = document.querySelector(".nav-center");
const navRight = document.querySelector(".nav-right");

if (hamburger && navCenter && navRight) {   // ✅ SAFE CHECK
  hamburger.addEventListener("click", () => {
    hamburger.classList.toggle("active");
    navCenter.classList.toggle("active");
    navRight.classList.toggle("active");
  });
}