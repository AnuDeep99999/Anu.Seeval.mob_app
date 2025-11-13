import React, { useEffect, useState } from "react";
import { View, Text, ActivityIndicator, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import API from "../../src/lib/api";
import { router } from "expo-router";


export default function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const getProfile = async () => {
      try {
        console.log("Fetching profile...");
        const res = await API.get("/auth/profile/"); // ✅ Fixed route

        console.log("Profile response:", res.data);

        setUser(res.data);
      } catch (err: any) {
        console.log("Profile fetch error:", err.response?.data || err);

        Alert.alert("Session expired", "Please log in again.");
        router.replace("/login");
      } finally {
        setLoading(false);
      }
    };

    getProfile();
  }, []);

  if (loading) {
    return (
      <SafeAreaView className="flex-1 items-center justify-center bg-primary">
        <ActivityIndicator size="large" color="#fff" />
      </SafeAreaView>
    );
  }

  if (!user) return null; // Redirected

  return (
    <SafeAreaView className="flex-1 items-center justify-center bg-primary">
      <Text className="text-3xl text-white font-pbold">Profile</Text>
      <Text className="text-white mt-4">
        Welcome, {user.name || user.email}
      </Text>
    </SafeAreaView>
  );
}
