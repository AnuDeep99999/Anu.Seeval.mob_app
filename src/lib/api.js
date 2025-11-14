// src/lib/api.js
import axios from "axios";
import AsyncStorage from "@react-native-async-storage/async-storage";
import Constants from "expo-constants";
import { Platform } from "react-native";

/*
  Strategy:
   1. Prefer EXPO_PUBLIC_API_URL from app.json extras (explicit).
   2. If not provided, use LAN_FALLBACK (physical device).
   3. If running in dev on Android emulator (not a real device), use 10.0.2.2.
*/

const extra = (Constants.expoConfig && Constants.expoConfig.extra) || {};
const envUrlRaw = extra.EXPO_PUBLIC_API_URL || null;
const envUrl = envUrlRaw ? String(envUrlRaw).trim().replace(/\/+$/, "") : null;

// update this to your host machine LAN IP when testing on a real phone
const LAN_FALLBACK = "http://192.168.55.102:8000/api";

let BASE_URL = envUrl || LAN_FALLBACK || "http://127.0.0.1:8000/api";

// Use emulator host mapping when appropriate
const isAndroid = Platform.OS === "android";
const isDevice = typeof Constants.isDevice !== "undefined" ? Constants.isDevice : true;
const isDev = typeof __DEV__ !== "undefined" ? __DEV__ : false;

if (!envUrl && isDev && isAndroid && isDevice === false) {
  // AVD emulator -> host machine's 127.0.0.1 is available at 10.0.2.2
  BASE_URL = "http://10.0.2.2:8000/api";
}

// normalize trailing slash
if (BASE_URL.endsWith("/")) BASE_URL = BASE_URL.slice(0, -1);

console.log("✅ API Base URL (final):", BASE_URL);

const API = axios.create({
  baseURL: BASE_URL,
  timeout: 30000, // 30s (safer for AI calls)
  headers: { "Content-Type": "application/json" },
});

// attach auth token if present
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

// verbose response/error logging for debugging emulator/network issues
API.interceptors.response.use(
  (res) => {
    console.log(`[API] ${res.status} ${String(res.config.method).toUpperCase()} ${res.config.url}`);
    return res;
  },
  (err) => {
    try {
      const serial = err && typeof err.toJSON === "function" ? err.toJSON() : err;
      console.log("[API] ERROR:", JSON.stringify(serial));
      if (err.config) {
        console.log("[API] request:", {
          url: err.config.url,
          baseURL: err.config.baseURL,
          method: err.config.method,
        });
      }
      if (err.response) {
        console.log("[API] response.status:", err.response.status);
        console.log("[API] response.data:", err.response.data);
      } else if (err.request) {
        console.log("[API] no response received; request was sent (err.request present).");
      } else {
        console.log("[API] message:", err.message);
      }
    } catch (e) {
      console.log("[API] ERROR logging failure", e);
    }
    return Promise.reject(err);
  }
);

export default API;
