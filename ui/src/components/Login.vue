<template>
  <div class="main-container">
    <!-- Login Button -->
    <Button
      v-if="!dataStore.isLoggedIn"
      class="p-button-sm p-button-outlined"
      @click="dataStore.showLoginDialog = true"
    >
      <i class="pi pi-user mr-2"></i>Login / Register
    </Button>

    <!-- Display username and logout button if logged in -->
    <div v-else class="user-info">
      <span class="username-display">Hello, {{ dataStore.username }}</span>
      <Button
        @click="handleLogout"
        class="p-button-danger p-button-sm p-button-text logout-button"
      >
        <i class="pi pi-sign-out" />
      </Button>
    </div>

    <!-- Dialog for Login and Register -->
    <Dialog
      v-model:visible="dataStore.showLoginDialog"
      :header="dataStore.isRegistering ? 'Register' : 'Login'"
      modal
      class="auth-dialog"
    >
      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="p-fluid flex flex-column gap-3">
          <div class="p-field">
            <label for="username" class="field-label">{{
              dataStore.isRegistering ? "Choose a Username" : "Username"
            }}</label>
            <InputText
              class="mt-1 auth-input"
              id="username"
              v-model="usernameInput"
              placeholder="Enter username"
            />
          </div>
          <div class="p-field">
            <label for="password" class="field-label">{{
              dataStore.isRegistering ? "Choose a Password" : "Password"
            }}</label>
            <Password
              class="my-1 auth-input"
              id="password"
              v-model="passwordInput"
              toggleMask
              :feedback="false"
              placeholder="Enter password"
            />
          </div>
        </div>

        <div class="auth-actions">
          <Button
            type="submit"
            class="p-button-primary mt-3 mb-2"
            :disabled="!usernameInput || !passwordInput"
          >
            <i v-if="dataStore.isRegistering" class="pi pi-user-plus mr-2"></i>
            <i v-else class="pi pi-sign-in mr-2"></i>
            {{ dataStore.isRegistering ? "Register" : "Login" }}
          </Button>
        </div>

        <p v-if="errorMessage && !dataStore.isLoggedIn" class="error-message">
          <i class="pi pi-exclamation-circle mr-2"></i>
          {{ errorMessage }}
        </p>

        <!-- Toggle between Login and Register -->
        <div class="auth-toggle">
          <a href="#" @click.prevent="toggleForm" class="toggle-link">
            {{
              dataStore.isRegistering
                ? "Already have an account? Login here"
                : "Don't have an account? Register here"
            }}
          </a>
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { defineEmits } from "vue";
import { useDataStore } from "@/stores/dataStore";
import Button from "primevue/button";
import Dialog from "primevue/dialog";
import InputText from "primevue/inputtext";
import Password from "primevue/password";

const dataStore = useDataStore();

const emit = defineEmits(["loggedIn"]);

const usernameInput = ref("");
const passwordInput = ref("");
const errorMessage = ref("");

const handleSubmit = () => {
  if (dataStore.isRegistering) {
    handleRegister();
  } else {
    handleLogin();
  }
};

const checkLoginStatus = () => {
  const token = localStorage.getItem("token");
  if (token) {
    const payload = JSON.parse(atob(token.split(".")[1]));
    dataStore.username = payload.username;
    dataStore.userId = payload.id;
    dataStore.isLoggedIn = true;
  }
};

const handleLogin = async () => {
  try {
    const response = await fetch(`${dataStore.backendServer}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: usernameInput.value,
        password: passwordInput.value,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      errorMessage.value = "";
      localStorage.setItem("token", data.token);
      checkLoginStatus(); // Update the UI to reflect login state
      dataStore.showLoginDialog = false;
    } else {
      errorMessage.value = data.message || "Login failed";
    }
  } catch (error) {
    errorMessage.value = "An error occurred";
  }
};

const handleRegister = async () => {
  try {
    const response = await fetch(`${dataStore.backendServer}/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: usernameInput.value,
        password: passwordInput.value,
      }),
    });

    if (response.ok) {
      errorMessage.value = "Registration successful! Please log in.";
      toggleForm(); // Switch to login form
    } else {
      const data = await response.json();
      errorMessage.value = data.message || "Registration failed";
    }
  } catch (error) {
    errorMessage.value = "An error occurred";
  }
};

// Handle logout
const handleLogout = () => {
  localStorage.removeItem("token");
  dataStore.isLoggedIn = false;
  dataStore.username = "";
  dataStore.userId = "";
};

// Toggle between login and register forms
const toggleForm = () => {
  dataStore.isRegistering = !dataStore.isRegistering;
  errorMessage.value = "";
};

checkLoginStatus();
</script>

<style scoped>
.main-container {
  padding: 0;
}

.username-display {
  margin-right: 10px;
  font-weight: 600;
  color: #4361ee;
  line-height: 1;
  font-size: 0.875rem;
}

.user-info {
  display: flex;
  align-items: center;
  background-color: rgba(67, 97, 238, 0.05);
  padding: 0.25rem 1rem;
  border-radius: 8px;
  line-height: 1;
}

.auth-form {
  padding: 0.5rem;
  width: 100%;
}

.p-fluid {
  width: 100%;
  margin: 0 auto;
}

.field-label {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  display: block;
}

.auth-input :deep(.p-inputtext) {
  border-radius: 8px;
  border: 1px solid #e9ecef;
  padding: 0.75rem;
  transition: all 0.2s;
}

.auth-input :deep(.p-inputtext:focus) {
  border-color: #4361ee;
  box-shadow: 0 0 0 1px rgba(67, 97, 238, 0.2);
}

.auth-input :deep(.p-password-input) {
  width: 100%;
}

.auth-actions {
  display: flex;
  justify-content: center;
  width: 100%;
}

/* Match the primary button styling from the main app */
.auth-actions :deep(.p-button.p-button-primary) {
  background-color: #4361ee;
  border-color: #4361ee;
  color: white;
  font-weight: 500;
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.auth-actions :deep(.p-button.p-button-primary:hover) {
  background-color: #3a56d4;
  border-color: #3a56d4;
  box-shadow: 0 4px 8px rgba(67, 97, 238, 0.2);
}

.auth-actions :deep(.p-button.p-button-primary:focus) {
  box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
}

.auth-actions :deep(.p-button.p-button-primary:disabled) {
  background-color: #c7d2fe;
  border-color: #c7d2fe;
  color: #6b7280;
}

.error-message {
  color: #ef4444;
  font-size: 0.9rem;
  margin: 0.5rem 0;
  padding: 0.5rem;
  background-color: rgba(239, 68, 68, 0.1);
  border-radius: 8px;
  display: flex;
  align-items: center;
}

.auth-toggle {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.toggle-link {
  color: #4361ee;
  text-decoration: none;
  transition: all 0.2s;
}

.toggle-link:hover {
  text-decoration: underline;
  color: #2c3e50;
}

:deep(.p-dialog) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

:deep(.p-dialog-header) {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  padding: 1.25rem 1.5rem;
}

:deep(.p-dialog-title) {
  font-weight: 600;
  color: #2c3e50;
}

:deep(.p-dialog-content) {
  padding: 1.5rem;
}

/* Add custom styling for the logout button */
.logout-button {
  padding: 0.25rem 0.5rem; /* Reduce padding from default */
}
</style>
