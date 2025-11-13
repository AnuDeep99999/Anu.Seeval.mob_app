import { View, Text, Pressable, Image, ImageBackground } from "react-native";
import { Link } from "expo-router";
import { LinearGradient } from "expo-linear-gradient";
import { Ionicons } from "@expo/vector-icons";
import Animated, { FadeIn } from "react-native-reanimated";
import { SafeAreaView } from "react-native-safe-area-context";
import images from '@/constants/images';
export default function Index() {
  return (
    <SafeAreaView style={{ flex: 1 }}>
      <ImageBackground
        source={images.homepage}  
        style={{ flex: 1 }}
        resizeMode="cover"
      >
        <LinearGradient
          colors={["rgba(79,172,254,0.7)", "rgba(0,242,254,0.7)"]}
          style={{
            flex: 1,
            alignItems: "center",
            justifyContent: "center",
            paddingHorizontal: 24,
          }}
        >
          <Animated.View
            entering={FadeIn.duration(1000)}
            style={{ alignItems: "center", width: "100%" }}
          >
            <Image
              source={images.logo}  
              style={{ width: 200, height: 100, marginBottom: 16 }}
              resizeMode="contain"
            />

            <Text style={{ fontSize: 32, fontWeight: "800", color: "white", marginBottom: 32 }}>
              Welcome, Anudeep
            </Text>

            <Link href="/login" asChild>
              <Pressable style={{
                backgroundColor: "rgba(255,255,255,0.2)",
                borderWidth: 1,
                borderColor: "rgba(255,255,255,0.3)",
                paddingHorizontal: 32,
                paddingVertical: 16,
                borderRadius: 9999,
                marginBottom: 16,
              }}>
                <View style={{ flexDirection: "row", alignItems: "center" }}>
                  <Ionicons name="log-in-outline" size={24} color="white" />
                  <Text style={{ color: "white", fontWeight: "600", fontSize: 18, marginLeft: 8 }}>
                    Login
                  </Text>
                </View>
              </Pressable>
            </Link>

            <Link href="/register" asChild>
              <Pressable style={{
                backgroundColor: "rgba(255,255,255,0.2)",
                borderWidth: 1,
                borderColor: "rgba(255,255,255,0.3)",
                paddingHorizontal: 32,
                paddingVertical: 16,
                borderRadius: 9999,
                marginBottom: 16,
              }}>
                <View style={{ flexDirection: "row", alignItems: "center" }}>
                  <Ionicons name="person-add-outline" size={24} color="white" />
                  <Text style={{ color: "white", fontWeight: "600", fontSize: 18, marginLeft: 8 }}>
                    Register
                  </Text>
                </View>
              </Pressable>
            </Link>

            <Link href="/profile" asChild>
              <Pressable style={{
                backgroundColor: "rgba(255,255,255,0.2)",
                borderWidth: 1,
                borderColor: "rgba(255,255,255,0.3)",
                paddingHorizontal: 32,
                paddingVertical: 16,
                borderRadius: 9999,
              }}>
                <View style={{ flexDirection: "row", alignItems: "center" }}>
                  <Ionicons name="person-circle-outline" size={24} color="white" />
                  <Text style={{ color: "white", fontWeight: "600", fontSize: 18, marginLeft: 8 }}>
                    Profile
                  </Text>
                </View>
              </Pressable>
            </Link>

            <Link href="/mcq" asChild>
            <Pressable style={{
             backgroundColor: "rgba(255,255,255,0.2)",
             borderWidth: 1,
             borderColor: "rgba(255,255,255,0.3)",
             paddingHorizontal: 32,
             paddingVertical: 16,
             borderRadius: 9999,
             marginTop: 16,
   }}>
          <View style={{ flexDirection: "row", alignItems: "center" }}>
          <Ionicons name="document-text-outline" size={24} color="white" />
          <Text style={{ color: "white", fontWeight: "600", fontSize: 18, marginLeft: 8 }}>
            Generate MCQs
          </Text>
      </View>
      </Pressable>
  </Link>


          </Animated.View>
        </LinearGradient>
      </ImageBackground>
    </SafeAreaView>
  );
}

