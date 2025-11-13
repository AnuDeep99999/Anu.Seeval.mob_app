// app/_layout.tsx
import 'react-native-reanimated';   // must be first
import './global.css';

import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Screen name="(auth)/login" options={{ headerShown: false }} />
      <Stack.Screen name="(auth)/register" options={{ headerShown: false }} />
      <Stack.Screen name="mcq" options={{ headerShown: true, title: 'Generate MCQs' }} />
      <Stack.Screen name="profile/index" options={{ headerShown: true, title: 'Profile' }} />
    </Stack>
  );
}
