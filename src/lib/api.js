// src/lib/api.js
import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import Constants from "expo-constants";
import { Platform } from "react-native";

/**
 * Source of base URL:
 * 1. EXPO_PUBLIC_API_URL from app.json
 * 2. Android emulator override (10.0.2.2)
 * 3. LAN fallback
 */

const extra = (Constants.expoConfig && Constants.expoConfig.extra) || {};
const envUrl = extra.EXPO_PUBLIC_API_URL ? String(extra.EXPO_PUBLIC_API_URL).trim() : null;

// Your LAN fallback
const LAN_FALLBACK = "http://192.168.55.150:8000/api";

let BASE_URL = envUrl || LAN_FALLBACK;

// Android emulator override (auto in dev mode)
if (__DEV__ && Platform.OS === "android") {
  BASE_URL = "http://10.0.2.2:8000/api"; // AVD emulator → host machine localhost
  // For Genymotion: BASE_URL = "http://10.0.3.2:8000/api";
}

// Normalize trailing slash
if (BASE_URL.endsWith("/")) BASE_URL = BASE_URL.slice(0, -1);

console.log("✅ API Base URL:", BASE_URL);

const API = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

// Attach token
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
  (error) => Promise.reject(error)
);

// Verbose logging
API.interceptors.response.use(
  (res) => {
    console.log(`[API] ${res.status} ${res.config.method?.toUpperCase()} ${res.config.url}`);
    return res;
  },
  (err) => {
    try {
      const serialized = typeof err.toJSON === "function" ? err.toJSON() : err;
      console.log("[API] ERROR toJSON:", JSON.stringify(serialized));
    } catch {
      console.log("[API] ERROR (fallback):", err?.message, err);
    }
    return Promise.reject(err);
  }
);

export default API;
