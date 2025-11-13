import React, { useState } from "react";
import { Text, Alert, ScrollView } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import FormField from "../../src/components/FormField";
import CustomButton from "../../src/components/CustomButton";
export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = () => {
    setIsLoading(true);
    // Fake API
    setTimeout(() => {
      setIsLoading(false);
      Alert.alert("Registered!", `Name: ${form.name}\nEmail: ${form.email}`);
    }, 1000);
  };

  return (
    <SafeAreaView className="flex-1 bg-primary px-4">
      <ScrollView contentContainerStyle={{ flexGrow: 1 }} className="justify-center">
        <Text className="text-3xl text-white font-pbold mb-8">Register</Text>

        <FormField
          title="Name"
          value={form.name}
          placeholder="Enter your name"
          handleChangeText={(value: string) => handleChange("name", value)}
          otherStyles="mb-5"
        />

        <FormField
          title="Email"
          value={form.email}
          placeholder="Enter your email"
          handleChangeText={(value: string) => handleChange("email", value)}
          otherStyles="mb-5"
        />

        <FormField
          title="Password"
          value={form.password}
          placeholder="Enter your password"
          handleChangeText={(value: string) => handleChange("password", value)}
          otherStyles="mb-8"
        />

        <CustomButton
          title="Sign Up"
          handlePress={handleSubmit}
          isLoading={isLoading}
          containerStyles="w-full"
        />
      </ScrollView>
    </SafeAreaView>
  );
}
