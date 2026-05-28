import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Linking } from 'react-native';

export default function ExpertBridge() {
  const [isStuck, setIsStuck] = useState(false);

  const openExpertCall = () => {
    // Kendi ismine özel Jitsi odası linki (bunu kendi adına göre değiştirebilirsin)
    const roomUrl = 'https://meet.jit.si/nokta-nokta-bridge-efe';
    Linking.openURL(roomUrl);
  };

  return (
    <View style={styles.container}>
      <Text style={styles.infoText}>
        Agent Durumu: {isStuck ? '🔴 STUCK (Çözülemiyor)' : '🟢 NORMAL'}
      </Text>

      {!isStuck && (
        <TouchableOpacity 
          style={styles.testButton} 
          onPress={() => setIsStuck(true)}
        >
          <Text style={styles.buttonText}>Simülasyon: Agent'ı STUCK Yap</Text>
        </TouchableOpacity>
      )}

      {isStuck && (
        <TouchableOpacity 
          style={styles.callButton} 
          onPress={openExpertCall}
        >
          <Text style={styles.buttonText}>📞 Uzmana Bağlan (WebRTC)</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20, alignItems: 'center', backgroundColor: '#2a2a2a', borderRadius: 10, margin: 10 },
  infoText: { color: '#fff', fontSize: 16, marginBottom: 15 },
  testButton: { backgroundColor: '#f59e0b', padding: 12, borderRadius: 8 },
  callButton: { backgroundColor: '#ef4444', padding: 15, borderRadius: 8, width: '100%', alignItems: 'center' },
  buttonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 }
});