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
    backendServer: 'http://webserverloadbalancer-248097766.us-east-2.elb.amazonaws.com/api'
  }),
  
  actions: {

  }
})
