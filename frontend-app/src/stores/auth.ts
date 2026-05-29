import { computed, reactive } from "vue";

import { clearToken, login as loginRequest, readToken, saveToken } from "@/api/client";

const USERNAME_KEY = "lithiumcraft.username";

const state = reactive({
  token: readToken(),
  username: localStorage.getItem(USERNAME_KEY) || ""
});

export const authStore = {
  state,
  isAuthenticated: computed(() => Boolean(state.token)),
  async login(username: string, password: string) {
    const response = await loginRequest({ username, password });
    saveToken(response.access_token);
    localStorage.setItem(USERNAME_KEY, username);
    state.token = response.access_token;
    state.username = username;
  },
  logout() {
    clearToken();
    localStorage.removeItem(USERNAME_KEY);
    state.token = null;
    state.username = "";
  }
};
