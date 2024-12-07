import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useDataStore = defineStore('dataStore', {
  state: () => ({ 
    showLoginDialog: false,
    isRegistering: false,
    userId: '',
    isLoggedIn: false,
    username: '',

    generateImage: true,
    backendServer: 'https://robbiehume.com/api'
  }),
  
  actions: {

  }
})
