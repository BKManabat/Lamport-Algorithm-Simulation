function updateResult(input) {
  location.href = `/encode/${input}`;
}

function clearField() {
  document.getElementById("floatingTextarea2").value = "";
  document.getElementById("display").innerHTML = "";
}

function scrollUp() {
  $('html, body').animate({scrollTop:0});
}

$(window).scroll(function() {
  if ($(window).scrollTop() > 600) {
    $('#backtoTop').addClass('show');
    $('#backtoTop').removeClass('remove');
  } else {
    $('#backtoTop').addClass('remove');
    $('#backtoTop').removeClass('show');
  }
});

let slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
  showSlides(slideIndex += n);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  let dots = document.getElementsByClassName("dot");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";
  dots[slideIndex-1].className += " active";
} 

function jumpTo(i) {
  $("#carouselId").carousel(i);
}