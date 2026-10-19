// =============================================================================
// FILE: static/js/script.js
// -----------------------------------------------------------------------------
// PURPOSE:  The site's shared front-end JavaScript. It adds small interactive
//           behaviours that run in the visitor's browser after a page loads.
// ROLE:     Included on every page via base.html (and several standalone pages).
//           Everything is "progressive enhancement": if an element a block needs
//           isn't on the page, that block safely does nothing (note the `if`
//           guards), so the same file works on every page.
// FEATURES:  - Mobile menu open/close (and auto-close on scroll)
//            - Keep number inputs within their max value
//            - Property image gallery: click thumbnails, next/prev buttons, zoom
//            - FAQ accordion (expand/collapse)
//            - Show a one-time alert for role messages and fill the footer year
// DEPENDS:  Specific CSS classes/IDs present in the templates (e.g. #menu-btn,
//           #mainImage, .gallery img). No external libraries are used.
// =============================================================================

// =========================
// MENU TOGGLE (SAFE)
// =========================
// Find the mobile menu and its toggle button; only wire them up if both exist.
const menu = document.querySelector('.header .menu');
const menuBtn = document.querySelector('#menu-btn');

if(menu && menuBtn){
   // Clicking the button toggles the 'active' class that shows/hides the menu.
   menuBtn.onclick = () => {
      menu.classList.toggle('active');
   };

   // Close the menu whenever the page is scrolled (better mobile UX).
   window.addEventListener('scroll', () => {
      menu.classList.remove('active');
   });
}


// =========================
// NUMBER INPUT LIMIT FIX
// =========================
// For every number input, clamp the typed value to its 'max' attribute so users
// can't enter a value above the allowed maximum (e.g. bedrooms, price).
document.querySelectorAll('input[type="number"]').forEach(input => {
   input.addEventListener("input", () => {
      if(input.max){
         input.value = Math.min(input.value, input.max);
      }
   });
});


// =========================
// PROPERTY IMAGE SYSTEM
// (CLICK + SLIDER + ZOOM)
// =========================
// Only runs on the property detail page, which has #mainImage and .gallery img.
const mainImage = document.getElementById("mainImage");
const thumbnails = document.querySelectorAll(".gallery img");
const nextBtn = document.getElementById("nextBtn");
const prevBtn = document.getElementById("prevBtn");

if(mainImage && thumbnails.length > 0){

   let currentIndex = 0;
   const images = Array.from(thumbnails);

   // CLICK THUMBNAIL
   // Clicking a thumbnail shows that image in the main view and updates the index.
   images.forEach((img, index) => {
      img.addEventListener("click", function(){
         mainImage.src = this.src;
         currentIndex = index;
      });
   });

   // NEXT BUTTON
   // Advance to the next image, wrapping around to the first at the end.
   if(nextBtn){
      nextBtn.addEventListener("click", () => {
         currentIndex = (currentIndex + 1) % images.length;
         mainImage.src = images[currentIndex].src;
      });
   }

   // PREVIOUS BUTTON
   // Go back one image, wrapping to the last when at the start.
   if(prevBtn){
      prevBtn.addEventListener("click", () => {
         currentIndex = (currentIndex - 1 + images.length) % images.length;
         mainImage.src = images[currentIndex].src;
      });
   }

   // ZOOM EFFECT
   // As the mouse moves over the main image, zoom to 2x centered on the cursor.
   mainImage.addEventListener("mousemove", function(e){
      const rect = this.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;

      this.style.transformOrigin = x + "% " + y + "%";
      this.style.transform = "scale(2)";
   });

   // Reset the zoom back to normal when the mouse leaves the image.
   mainImage.addEventListener("mouseleave", function(){
      this.style.transform = "scale(1)";
   });
}


// =========================
// FAQ TOGGLE
// =========================
// Clicking an FAQ question toggles the 'active' class on its box to show/hide
// the answer (an accordion).
document.querySelectorAll('.faq .box-container .box h3').forEach(head => {
   head.addEventListener("click", () => {
      head.parentElement.classList.toggle('active');
   });
});


// =========================
// ROLE MESSAGE ALERT
// =========================
// After the DOM is ready, look for any .role-message elements. If one carries a
// data-message attribute, show it as a browser alert and log the user type.
document.addEventListener('DOMContentLoaded', () => {
   const messages = document.querySelectorAll('.role-message');

   messages.forEach(msg => {
      const messageText = msg.dataset.message;
      const userType = msg.dataset.userType;

      if(messageText){
         alert(messageText);
         console.log(`User type: ${userType}`);
      }
   });
});