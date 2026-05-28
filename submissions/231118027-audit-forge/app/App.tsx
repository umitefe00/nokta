import React, { useState } from 'react';
import { Text, View, StyleSheet } from 'react-native';
import { NavigationContainer, useNavigationContainerRef } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { captureScreen, captureRef } from 'react-native-view-shot';

import VoiceVisualizer from './VoiceVisualizer';
import ExpertBridge from './ExpertBridge';

// Ekranlarımız
import HomeScreen from './screens/HomeScreen';
import ProfileScreen from './screens/ProfileScreen';
import SettingsScreen from './screens/SettingsScreen';

// Audit Widget ve Storage
import { AuditWidget } from '@xtatistix/mobile-audit';
import { auditStorage } from './auditStorage';

const Stack = createNativeStackNavigator();

export default function App() {
  const navigationRef = useNavigationContainerRef();
  const [routeName, setRouteName] = useState('Home');

  return (
    <View style={{ flex: 1, backgroundColor: '#1e1e1e' }}>
      
      {/* Üst Başlık Alanı (Avatar yerine profesyonel bir duruş) */}
      <View style={styles.headerBanner}>
        <Text style={styles.headerTitle}>🎙️ NOKTA FORGE CONTROL PANEL</Text>
        <Text style={styles.headerSubtitle}>Geliştirici: 231118027 - Efe</Text>
      </View>

      {/* Ses Görselleştirici (FFT & STT) */}
      <View style={{ paddingBottom: 10 }}>
        <VoiceVisualizer />
      </View>

      {/* Uzmana Bağlan Butonu (WebRTC Köprüsü) */}
      <View style={{ paddingBottom: 10 }}>
        <ExpertBridge />
      </View>

      {/* Uygulama Navigasyonu */}
      <NavigationContainer
        ref={navigationRef}
        onStateChange={() => {
          // @ts-ignore - TypeScript navigasyon ismini bulamadığı için susturuyoruz
          const currentRouteName = navigationRef.getCurrentRoute()?.name;
          if (currentRouteName) {
            setRouteName(currentRouteName);
          }
        }}
      >
        <Stack.Navigator initialRouteName="Home">
          <Stack.Screen name="Home" component={HomeScreen} options={{ title: 'Ana Sayfa' }} />
          <Stack.Screen name="Profile" component={ProfileScreen} options={{ title: 'Profil Ekranı' }} />
          <Stack.Screen name="Settings" component={SettingsScreen} options={{ title: 'Ayarlar' }} />
        </Stack.Navigator>
      </NavigationContainer>

      {/* Audit Widget (Raporlama Döngüsü) */}
      <AuditWidget
        appName="NoktaForge"
        initialPosition={{ bottom: 100, right: 16 }}
        deps={{
          captureScreen: async () => {
            try {
              return await captureScreen({ format: 'png', result: 'tmpfile' });
            } catch (error) {
              return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="; 
            }
          },
          captureRef: async (ref) => {
            try {
              return await captureRef(ref, { format: 'png', result: 'tmpfile' });
            } catch (error) {
              return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
            }
          },
          writeFile: async (filename, content) => {
            console.log("\n\n====== 🚀 BULDĞUN HATANIN MD RAPORU ======\n");
            console.log(content);
            console.log("\n==========================================\n\n");
            return "web-dummy-uri";
          },
          writeFileBinary: async (filename: string, base64: string) => {
            const dir = FileSystem.documentDirectory || '';
            const uri = dir + filename;
            // @ts-ignore
            await FileSystem.writeAsStringAsync(uri, base64, {
             encoding: FileSystem.EncodingType.Base64,
            });
            return uri;
          },
          shareFile: (uri) => Sharing.shareAsync(uri),
          storage: auditStorage,
          currentScreen: routeName,
          reporterId: '231118027-Efe',
          BugIcon: <Text style={{ fontSize: 22 }}>🐛</Text>,
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  headerBanner: {
    backgroundColor: '#121212',
    paddingVertical: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#333'
  },
  headerTitle: {
    color: '#10b981',
    fontSize: 18,
    fontWeight: 'bold',
    letterSpacing: 1
  },
  headerSubtitle: {
    color: '#aaa',
    fontSize: 12,
    marginTop: 4
  }
});