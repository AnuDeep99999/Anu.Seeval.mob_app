// src/lib/api.js
import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import Constants from "expo-constants";
import { Platform } from "react-native";

const extra = (Constants.expoConfig && Constants.expoConfig.extra) || {};
const envUrl = extra.EXPO_PUBLIC_API_URL ? String(extra.EXPO_PUBLIC_API_URL).trim() : null;

// Fallback is your LAN IP — keep in sync with app.json
const LAN_FALLBACK = "http://192.168.55.102:8000/api";

let BASE_URL = envUrl || LAN_FALLBACK;

// emulator override only when there is no env override and running in DEV on android emulator
if (!envUrl && __DEV__ && Platform.OS === "android" && Constants.isDevice === false) {
  BASE_URL = "http://10.0.2.2:8000/api";
}

// strip trailing slash
if (BASE_URL.endsWith("/")) BASE_URL = BASE_URL.slice(0, -1);

console.log("✅ API Base URL (final):", BASE_URL);

const API = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

API.interceptors.request.use(
  async (config) => {
    try {
      const token = await AsyncStorage.getItem("access_token");
      if (token) {
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${token}`;
      }
    } catch (e) {
      console.warn("⚠️ Failed to read access token:", e);
    }
    return config;
  },
  (err) => Promise.reject(err)
);

API.interceptors.response.use(
  (res) => res,
  (err) => {
    try {
      console.log("[API] ERROR:", JSON.stringify(err.toJSON ? err.toJSON() : err));
    } catch {
      console.log("[API] ERROR:", err && err.message);
    }
    return Promise.reject(err);
  }
);

export default API;
