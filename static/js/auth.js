// Authentication JavaScript
class AuthManager {
  constructor() {
    this.initializeEventListeners();
    this.initializePasswordToggles();
    this.initializePasswordStrength();
  }

  initializeEventListeners() {
    // Login form
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
      loginForm.addEventListener("submit", this.handleLogin.bind(this));
    }

    // Register form
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
      registerForm.addEventListener("submit", this.handleRegister.bind(this));

      // Real-time validation
      const confirmPassword = document.getElementById("confirmPassword");
      if (confirmPassword) {
        confirmPassword.addEventListener(
          "input",
          this.validatePasswordMatch.bind(this)
        );
      }

      // Age calculation from date of birth
      const dateOfBirth = document.getElementById("dateOfBirth");
      const ageInput = document.getElementById("age");
      if (dateOfBirth && ageInput) {
        dateOfBirth.addEventListener("change", () => {
          const age = this.calculateAge(dateOfBirth.value);
          if (age) {
            ageInput.value = age;
          }
        });
      }
    }

    // Google authentication
    const googleBtn = document.querySelector(".auth-btn.google");
    if (googleBtn) {
      googleBtn.addEventListener("click", this.handleGoogleAuth.bind(this));
    }
  }

  initializePasswordToggles() {
    const toggleButtons = document.querySelectorAll(".password-toggle");
    toggleButtons.forEach(button => {
      button.addEventListener("click", () => {
        const input = button.previousElementSibling;
        const icon = button.querySelector("i");

        if (input.type === "password") {
          input.type = "text";
          icon.classList.remove("fa-eye");
          icon.classList.add("fa-eye-slash");
        } else {
          input.type = "password";
          icon.classList.remove("fa-eye-slash");
          icon.classList.add("fa-eye");
        }
      });
    });
  }

  initializePasswordStrength() {
    const passwordInput = document.getElementById("password");
    if (passwordInput) {
      passwordInput.addEventListener(
        "input",
        this.checkPasswordStrength.bind(this)
      );
    }
  }

  async handleLogin(e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = form.querySelector(".auth-btn.primary");
    const formData = new FormData(form);

    // Show loading state
    this.showLoading(submitBtn);

    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: formData.get("email"),
          password: formData.get("password"),
          remember: formData.get("remember") === "on",
        }),
      });

      const data = await response.json();

      if (data.success) {
        this.showAlert("Login successful! Redirecting...", "success");
        setTimeout(() => {
          window.location.href = data.redirect || "/chat";
        }, 1000);
      } else {
        this.showAlert(
          data.message || "Login failed. Please try again.",
          "error"
        );
      }
    } catch (error) {
      this.showAlert("Network error. Please check your connection.", "error");
      console.error("Login error:", error);
    } finally {
      this.hideLoading(submitBtn);
    }
  }

  async handleRegister(e) {
    e.preventDefault();

    const form = e.target;
    const submitBtn = form.querySelector(".auth-btn.primary");
    const formData = new FormData(form);

    // Validate form
    if (!this.validateRegistrationForm(form)) {
      return;
    }

    // Show loading state
    this.showLoading(submitBtn);

    try {
      const response = await fetch("/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          firstName: formData.get("firstName"),
          lastName: formData.get("lastName"),
          email: formData.get("email"),
          phone: formData.get("phone"),
          dateOfBirth: formData.get("dateOfBirth"),
          gender: formData.get("gender"),
          age: parseInt(formData.get("age")),
          password: formData.get("password"),
          terms: formData.get("terms") === "on",
          newsletter: formData.get("newsletter") === "on",
        }),
      });

      const data = await response.json();

      if (data.success) {
        this.showAlert(
          "Account created successfully! Please check your email for verification.",
          "success"
        );
        setTimeout(() => {
          window.location.href = "/login";
        }, 2000);
      } else {
        this.showAlert(
          data.message || "Registration failed. Please try again.",
          "error"
        );
      }
    } catch (error) {
      this.showAlert("Network error. Please check your connection.", "error");
      console.error("Registration error:", error);
    } finally {
      this.hideLoading(submitBtn);
    }
  }

  async handleGoogleAuth() {
    try {
      this.showAlert("Redirecting to Google...", "info");
      // In a real implementation, this would redirect to Google OAuth
      window.location.href = "/auth/google";
    } catch (error) {
      this.showAlert(
        "Google authentication is not available at the moment.",
        "error"
      );
    }
  }

  validateRegistrationForm(form) {
    let isValid = true;

    // Clear previous validation
    this.clearValidationErrors(form);

    // Required fields validation
    const requiredFields = [
      "firstName",
      "lastName",
      "email",
      "dateOfBirth",
      "gender",
      "age",
      "password",
      "confirmPassword",
    ];

    requiredFields.forEach(fieldName => {
      const field = form.querySelector(`[name="${fieldName}"]`);
      if (!field.value.trim()) {
        this.showFieldError(
          field,
          `${this.formatFieldName(fieldName)} is required`
        );
        isValid = false;
      }
    });

    // Email validation
    const email = form.querySelector('[name="email"]');
    if (email.value && !this.isValidEmail(email.value)) {
      this.showFieldError(email, "Please enter a valid email address");
      isValid = false;
    }

    // Password validation
    const password = form.querySelector('[name="password"]');
    const confirmPassword = form.querySelector('[name="confirmPassword"]');

    if (password.value && password.value.length < 8) {
      this.showFieldError(
        password,
        "Password must be at least 8 characters long"
      );
      isValid = false;
    }

    if (password.value !== confirmPassword.value) {
      this.showFieldError(confirmPassword, "Passwords do not match");
      isValid = false;
    }

    // Age validation
    const age = form.querySelector('[name="age"]');
    const ageValue = parseInt(age.value);
    if (ageValue && (ageValue < 1 || ageValue > 120)) {
      this.showFieldError(age, "Please enter a valid age");
      isValid = false;
    }

    // Terms checkbox validation
    const terms = form.querySelector('[name="terms"]');
    if (!terms.checked) {
      this.showAlert(
        "You must agree to the Terms of Service to create an account.",
        "warning"
      );
      isValid = false;
    }

    return isValid;
  }

  validatePasswordMatch() {
    const password = document.getElementById("password");
    const confirmPassword = document.getElementById("confirmPassword");

    if (confirmPassword.value && password.value !== confirmPassword.value) {
      this.showFieldError(confirmPassword, "Passwords do not match");
    } else {
      this.clearFieldError(confirmPassword);
    }
  }

  checkPasswordStrength(e) {
    const password = e.target.value;
    const strengthElement = document.getElementById("passwordStrength");
    const strengthFill = strengthElement.querySelector(".strength-fill");
    const strengthText = strengthElement.querySelector(".strength-text");

    if (!password) {
      strengthElement.classList.remove("show");
      return;
    }

    strengthElement.classList.add("show");

    let score = 0;
    let feedback = "";

    // Length check
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;

    // Character variety checks
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;

    // Remove all strength classes
    strengthFill.classList.remove("weak", "medium", "strong");

    if (score < 3) {
      strengthFill.classList.add("weak");
      feedback = "Weak password";
    } else if (score < 5) {
      strengthFill.classList.add("medium");
      feedback = "Medium strength";
    } else {
      strengthFill.classList.add("strong");
      feedback = "Strong password";
    }

    strengthText.textContent = feedback;
  }

  calculateAge(dateOfBirth) {
    if (!dateOfBirth) return null;

    const today = new Date();
    const birthDate = new Date(dateOfBirth);
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (
      monthDiff < 0 ||
      (monthDiff === 0 && today.getDate() < birthDate.getDate())
    ) {
      age--;
    }

    return age;
  }

  isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  showFieldError(field, message) {
    const formGroup = field.closest(".form-group");
    formGroup.classList.add("error");
    formGroup.classList.remove("success");

    // Remove existing error message
    const existingError = formGroup.querySelector(".error-message");
    if (existingError) {
      existingError.remove();
    }

    // Add new error message
    const errorDiv = document.createElement("div");
    errorDiv.className = "error-message";
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    formGroup.appendChild(errorDiv);
  }

  clearFieldError(field) {
    const formGroup = field.closest(".form-group");
    formGroup.classList.remove("error");
    formGroup.classList.add("success");

    const errorMessage = formGroup.querySelector(".error-message");
    if (errorMessage) {
      errorMessage.remove();
    }
  }

  clearValidationErrors(form) {
    const errorGroups = form.querySelectorAll(".form-group.error");
    errorGroups.forEach(group => {
      group.classList.remove("error", "success");
      const errorMessage = group.querySelector(".error-message");
      if (errorMessage) {
        errorMessage.remove();
      }
    });
  }

  formatFieldName(fieldName) {
    return fieldName
      .replace(/([A-Z])/g, " $1")
      .replace(/^./, str => str.toUpperCase());
  }

  showLoading(button) {
    button.classList.add("loading");
    button.disabled = true;

    const btnText = button.querySelector(".btn-text");
    const btnLoader = button.querySelector(".btn-loader");

    if (btnText) btnText.style.opacity = "0";
    if (btnLoader) btnLoader.style.display = "block";
  }

  hideLoading(button) {
    button.classList.remove("loading");
    button.disabled = false;

    const btnText = button.querySelector(".btn-text");
    const btnLoader = button.querySelector(".btn-loader");

    if (btnText) btnText.style.opacity = "1";
    if (btnLoader) btnLoader.style.display = "none";
  }

  showAlert(message, type = "info") {
    const alertContainer = document.getElementById("alertContainer");
    const alert = document.createElement("div");
    alert.className = `alert ${type}`;

    const icon = this.getAlertIcon(type);
    alert.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;

    alertContainer.appendChild(alert);

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (alert.parentElement) {
        alert.style.animation = "slideOut 0.3s ease forwards";
        setTimeout(() => {
          if (alert.parentElement) {
            alert.remove();
          }
        }, 300);
      }
    }, 5000);
  }

  getAlertIcon(type) {
    const icons = {
      success: "fas fa-check-circle",
      error: "fas fa-exclamation-triangle",
      warning: "fas fa-exclamation-circle",
      info: "fas fa-info-circle",
    };
    return icons[type] || icons.info;
  }
}

// Initialize authentication manager when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new AuthManager();
});

// Utility functions
function showAlert(message, type = "info") {
  const authManager = new AuthManager();
  authManager.showAlert(message, type);
}
