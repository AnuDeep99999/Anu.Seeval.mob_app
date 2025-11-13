import React, { useState } from "react";
import { Text, TextInput, Button, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useRouter } from "expo-router";
import AsyncStorage from "@react-native-async-storage/async-storage";
import API from "@/lib/api";


export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert("Validation", "Please enter email and password");
      return;
    }

    setLoading(true);
    try {
      // DRF SimpleJWT default token endpoint
      const res = await API.post("/token/", {
        username: email, // SimpleJWT expects "username"
        password: password,
      });

      const { access, refresh } = res.data;
      await AsyncStorage.setItem("access_token", access);
      await AsyncStorage.setItem("refresh_token", refresh);

      Alert.alert("Login successful");
      router.replace("/profile");
    } catch (err: any) {
      console.log(err?.response?.data || err);
      Alert.alert("Login failed", err?.response?.data?.detail || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontSize: 24, marginBottom: 16 }}>Login</Text>

      <TextInput
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        style={{ borderWidth: 1, marginBottom: 12, padding: 8 }}
      />

      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{ borderWidth: 1, marginBottom: 12, padding: 8 }}
      />

      <Button title={loading ? "Logging in..." : "Login"} onPress={handleLogin} disabled={loading} />
    </SafeAreaView>
  );
}
