<template>
  <div class="main-container">
    <!-- Login Button -->
    <Button v-if="!dataStore.isLoggedIn" class="p-button-sm" label="" @click="dataStore.showLoginDialog = true" >
      Login / Register
    </Button>

    <!-- Display username and logout button if logged in -->
    <div v-else class="flex align-items-center">
      <span class="username-display">Hello, {{ dataStore.username }}</span>
      <Button @click="handleLogout" class="p-2 p-button-danger p-button-sm" style="width:fit-content; height: fit-content" >
        <i class="pi pi-sign-out text-red-"  style="font-size: 14px" />
      </Button>
    </div>

    <!-- Dialog for Login and Register -->
    <Dialog
      v-model:visible="dataStore.showLoginDialog"
      :header="dataStore.isRegistering ? 'Register' : 'Login'"
      modal
    >
      <!-- <form @submit.prevent="dataStore.isRegistering ? handleRegister : handleLogin"> -->
    <form @submit.prevent="handleSubmit">
        <div class="p-fluid flex flex-column gap-2">
          <div class="p-field">
            <label for="username">{{
              dataStore.isRegistering ? 'Choose a Username' : 'Username'
            }}</label>
            <InputText class="mt-1" id="username" v-model="usernameInput" />
          </div>
          <div class="p-field">
            <label for="password">{{
              dataStore.isRegistering ? 'Choose a Password' : 'Password'
            }}</label>
            <Password class="my-1" id="password" v-model="passwordInput" toggleMask :feedback="false" />
          </div>
        </div>
        <Button label="Submit" type="submit" class="p-mt-3 my-3" />
      </form>
      <p v-if="errorMessage && !dataStore.isLoggedIn" class="p-error">{{ errorMessage }}</p>

      <!-- Toggle between Login and Register -->
      <p class="mt-0">
        <a class="p-0" href="#" @click.prevent="toggleForm">
          {{
            dataStore.isRegistering
              ? 'Already have an account? Login here'
              : "Don't have an account? Register here"
          }}
        </a>
      </p>
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { defineEmits } from 'vue';
import { useDataStore } from '@/stores/dataStore';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';

const dataStore = useDataStore();

const emit = defineEmits(['loggedIn']);

const usernameInput = ref('');
const passwordInput = ref('');
const errorMessage = ref('');


const handleSubmit = () => {
  if (dataStore.isRegistering) {
    handleRegister()
  } else {
    handleLogin()
  }
}

const checkLoginStatus = () => {
  const token = localStorage.getItem('token');
  if (token) {
    const payload = JSON.parse(atob(token.split('.')[1]));
    dataStore.username = payload.username;
    dataStore.userId = payload.id
    dataStore.isLoggedIn = true;
  }
};

const handleLogin = async () => {
  try {
    const response = await fetch(`${dataStore.backendServer}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: usernameInput.value,
        password: passwordInput.value,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      errorMessage.value = ''
      localStorage.setItem('token', data.token);
      checkLoginStatus(); // Update the UI to reflect login state
      dataStore.showLoginDialog = false;
    } else {
      errorMessage.value = data.message || 'Login failed';
    }
  } catch (error) {
    errorMessage.value = 'An error occurred';
  }
};

const handleRegister = async () => {
  try {
    const response = await fetch(`${dataStore.backendServer}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: usernameInput.value,
        password: passwordInput.value,
      }),
    });

    if (response.ok) {
      errorMessage.value = 'Registration successful! Please log in.';
      toggleForm(); // Switch to login form
    } else {
      const data = await response.json();
      errorMessage.value = data.message || 'Registration failed';
    }
  } catch (error) {
    errorMessage.value = 'An error occurred';
  }
};

// Handle logout
const handleLogout = () => {
  localStorage.removeItem('token');
  dataStore.isLoggedIn = false;
  dataStore.username = '';
  dataStore.userId = '';
};

// Toggle between login and register forms
const toggleForm = () => {
  dataStore.isRegistering = !dataStore.isRegistering;
  errorMessage.value = '';
};

checkLoginStatus();
</script>

<style scoped>
.main-container {
  padding: 2rem;
}

.username-display {
  margin-right: 7px;
  font-weight: bold;
}

.p-fluid {
  width: 300px;
  margin: 0 auto;
}
</style>
