/**
 * Blood Donor Finder - Client-side JavaScript
 * Handles form validation, UI interactions, and alert dismissals
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Auto-dismiss or manual dismiss for flash alerts
  const alertCloseButtons = document.querySelectorAll(".alert-close");
  alertCloseButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const alertBox = this.closest(".alert");
      if (alertBox) {
        alertBox.style.opacity = "0";
        setTimeout(() => alertBox.remove(), 250);
      }
    });
  });

  // Auto-fade flash messages after 6 seconds
  const flashAlerts = document.querySelectorAll(".alert");
  if (flashAlerts.length > 0) {
    setTimeout(() => {
      flashAlerts.forEach((alert) => {
        alert.style.transition = "opacity 0.4s ease";
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 400);
      });
    }, 6000);
  }

  // 2. Client-side Registration Form Validation
  const donorForm = document.getElementById("donorRegisterForm");
  if (donorForm) {
    donorForm.addEventListener("submit", function (e) {
      let isValid = true;
      const errorMessages = [];

      const name = document.getElementById("name").value.trim();
      const age = parseInt(document.getElementById("age").value.trim(), 10);
      const gender = document.getElementById("gender").value;
      const bloodGroup = document.getElementById("blood_group").value;
      const phone = document.getElementById("phone").value.trim();
      const city = document.getElementById("city").value.trim();
      const area = document.getElementById("area").value.trim();

      // Name validation
      if (!name) {
        isValid = false;
        errorMessages.push("Please enter your full name.");
      }

      // Age validation (Blood donors must usually be 18 to 65 years old)
      if (isNaN(age) || age < 18 || age > 65) {
        isValid = false;
        errorMessages.push("Age must be between 18 and 65 years.");
      }

      // Gender validation
      if (!gender) {
        isValid = false;
        errorMessages.push("Please select a gender.");
      }

      // Blood group validation
      if (!bloodGroup) {
        isValid = false;
        errorMessages.push("Please select a blood group.");
      }

      // Phone validation (10 digits)
      const phoneRegex = /^[0-9]{10}$/;
      if (!phoneRegex.test(phone)) {
        isValid = false;
        errorMessages.push("Please enter a valid 10-digit phone number.");
      }

      // City validation
      if (!city) {
        isValid = false;
        errorMessages.push("Please enter your city.");
      }

      // Area validation
      if (!area) {
        isValid = false;
        errorMessages.push("Please enter your area or neighborhood.");
      }

      if (!isValid) {
        e.preventDefault();
        showClientError(errorMessages[0]);
      } else {
        const submitBtn = document.getElementById("submitDonorBtn");
        if (submitBtn) {
          submitBtn.innerHTML = "⏳ Registering Donor...";
          submitBtn.style.opacity = "0.75";
          submitBtn.style.pointerEvents = "none";
        }
      }
    });

    // Restrict phone input to numeric only and max 10 digits
    const phoneInput = document.getElementById("phone");
    if (phoneInput) {
      phoneInput.addEventListener("input", function () {
        this.value = this.value.replace(/[^0-9]/g, "").slice(0, 10);
      });
    }
  }

  // Helper function to show inline client error notification for registration form
  function showClientError(message) {
    let clientAlert = document.getElementById("clientAlertBox");
    if (!clientAlert) {
      clientAlert = document.createElement("div");
      clientAlert.id = "clientAlertBox";
      clientAlert.className = "alert alert-error";
      clientAlert.innerHTML = `
        <span>⚠️ ${message}</span>
        <button type="button" class="alert-close">&times;</button>
      `;
      const formWrapper = document.querySelector(".card-form-wrapper");
      if (formWrapper) {
        formWrapper.insertBefore(clientAlert, formWrapper.children[1]);
      }
      // Attach close handler
      clientAlert.querySelector(".alert-close").addEventListener("click", function () {
        clientAlert.remove();
      });
    } else {
      clientAlert.querySelector("span").textContent = "⚠️ " + message;
      clientAlert.style.display = "flex";
      clientAlert.style.opacity = "1";
    }

    // Scroll to alert
    clientAlert.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  // 3. Copy Phone Number to Clipboard with Toast Notification
  const copyButtons = document.querySelectorAll(".btn-copy");
  copyButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      const phone = this.getAttribute("data-phone");
      const name = this.getAttribute("data-name") || "Donor";

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(phone).then(() => {
          showToast(`📋 Copied ${name}'s number (${phone}) to clipboard!`);
          triggerButtonFeedback(this);
        }).catch(() => {
          fallbackCopyText(phone, name, this);
        });
      } else {
        fallbackCopyText(phone, name, this);
      }
    });
  });

  // Fallback for older browsers or non-secure contexts
  function fallbackCopyText(text, name, buttonElement) {
    const tempInput = document.createElement("input");
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    try {
      document.execCommand("copy");
      showToast(`📋 Copied ${name}'s number (${text}) to clipboard!`);
      triggerButtonFeedback(buttonElement);
    } catch (err) {
      showToast(`Phone: ${text}`);
    }
    document.body.removeChild(tempInput);
  }

  function triggerButtonFeedback(btn) {
    const originalText = btn.innerHTML;
    btn.innerHTML = "<span>✓ Copied!</span>";
    btn.classList.add("copied");
    setTimeout(() => {
      btn.innerHTML = originalText;
      btn.classList.remove("copied");
    }, 2000);
  }

  // Toast Notification Helper
  function showToast(message) {
    let toast = document.getElementById("toastNotification");
    if (!toast) {
      toast = document.createElement("div");
      toast.id = "toastNotification";
      toast.className = "toast-notification";
      document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.classList.add("show");

    clearTimeout(toast.timeoutId);
    toast.timeoutId = setTimeout(() => {
      toast.classList.remove("show");
    }, 3500);
  }

  // 4. Smart Call Handler & Desktop Call Modal
  const callModal = document.getElementById("callModal");
  const closeCallModal = document.getElementById("closeCallModal");
  const modalDonorName = document.getElementById("modalDonorName");
  const modalDonorMeta = document.getElementById("modalDonorMeta");
  const modalPhoneNumber = document.getElementById("modalPhoneNumber");
  const modalDialBtn = document.getElementById("modalDialBtn");
  const modalWhatsappBtn = document.getElementById("modalWhatsappBtn");
  const modalCopyBtn = document.getElementById("modalCopyBtn");

  const callButtons = document.querySelectorAll(".btn-call");
  callButtons.forEach((callBtn) => {
    callBtn.addEventListener("click", function (e) {
      e.preventDefault(); // Stop any browser page navigation / Chrome redirect

      const rawPhone = this.getAttribute("data-phone") || "";
      const name = this.getAttribute("data-name") || "Donor";
      const blood = this.getAttribute("data-blood") || "";
      const city = this.getAttribute("data-city") || "";
      const cleanPhone = rawPhone.replace(/[^0-9+]/g, "");

      if (!cleanPhone) {
        showToast("⚠️ Invalid phone number entered.");
        return;
      }

      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);

      if (isMobile) {
        // On mobile phones: directly trigger phone dialer without Chrome redirecting
        const dialLink = document.createElement("a");
        dialLink.href = "tel:" + cleanPhone;
        dialLink.style.display = "none";
        document.body.appendChild(dialLink);
        dialLink.click();
        setTimeout(() => dialLink.remove(), 500);
      } else {
        // On desktop/laptop: open Call Modal so Chrome NEVER leaves or redirects the page!
        if (callModal) {
          modalDonorName.textContent = name;
          modalDonorMeta.textContent = `Blood Group: ${blood} • City: ${city}`;
          modalPhoneNumber.textContent = cleanPhone;

          // Wire modal actions
          modalDialBtn.href = "tel:" + cleanPhone;
          modalWhatsappBtn.href = `https://wa.me/91${cleanPhone}?text=${encodeURIComponent(`Hello ${name}, I found your contact on Blood Donor Finder. We urgently need ${blood} blood in ${city}. Are you available to donate?`)}`;
          
          modalCopyBtn.onclick = function () {
            if (navigator.clipboard && navigator.clipboard.writeText) {
              navigator.clipboard.writeText(cleanPhone).then(() => {
                showToast(`📋 Copied ${name}'s number (${cleanPhone})!`);
                modalCopyBtn.innerHTML = "<span>✓ Copied!</span>";
                setTimeout(() => {
                  modalCopyBtn.innerHTML = "<span>📋 Copy Number to Dial on Phone</span>";
                }, 2000);
              });
            }
          };

          callModal.style.display = "flex";
        } else {
          showToast(`📞 Donor Phone: ${cleanPhone}`);
        }
      }
    });
  });

  // Close Call Modal Events
  if (closeCallModal && callModal) {
    closeCallModal.addEventListener("click", function () {
      callModal.style.display = "none";
    });

    callModal.addEventListener("click", function (e) {
      if (e.target === callModal) {
        callModal.style.display = "none";
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && callModal.style.display === "flex") {
        callModal.style.display = "none";
      }
    });
  }
});
