import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, TouchableOpacity, Text, TextInput } from 'react-native';

export default function VoiceVisualizer() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioLevel, setAudioLevel] = useState(0);
  const [transcript, setTranscript] = useState(''); // Sesin yazıya dökülmüş hali

  // Web Audio API referansları
  const audioContextRef = useRef<any>(null);
  const analyserRef = useRef<any>(null);
  const animationRef = useRef<number | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  
  // Speech-to-Text referansı
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Tarayıcı SpeechRecognition destekliyor mu kontrolü
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true; // Konuşma bitene kadar dinle
      recognitionRef.current.interimResults = true; // Eşzamanlı yazmaya çalış
      recognitionRef.current.lang = 'tr-TR'; // Türkçe algılama

      recognitionRef.current.onresult = (event: any) => {
        let currentTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          currentTranscript += event.results[i][0].transcript;
        }
        setTranscript(prev => prev + currentTranscript + ' ');
      };
    } else {
      console.warn("Tarayıcın Speech-To-Text desteklemiyor (Chrome veya Edge kullan).");
    }
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      analyserRef.current.fftSize = 256;
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const updateLevel = () => {
        analyserRef.current.getByteFrequencyData(dataArray);
        let sum = 0;
        for(let i = 0; i < bufferLength; i++) {
          sum += dataArray[i];
        }
        setAudioLevel((sum / bufferLength) / 100); 
        animationRef.current = requestAnimationFrame(updateLevel);
      };

      updateLevel();
      setIsRecording(true);
      setTranscript(''); // Yeni konuşmada eski metni temizle
      
      // Sesi yazıya çevirmeyi başlat
      if (recognitionRef.current) {
        recognitionRef.current.start();
      }

    } catch (err) {
      console.error("Mikrofon hatası:", err);
    }
  };

  const stopRecording = () => {
    if (animationRef.current) cancelAnimationFrame(animationRef.current);
    if (streamRef.current) streamRef.current.getTracks().forEach(track => track.stop());
    if (audioContextRef.current) audioContextRef.current.close();
    
    // Sesi yazıya çevirmeyi durdur
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    setIsRecording(false);
    setAudioLevel(0);
  };

  return (
    <View style={styles.container}>
      {/* Sesi Yazıya Dökme (STT) Alanı */}
      <View style={styles.transcriptContainer}>
        <Text style={styles.label}>🎙️ Dikte Edilen Rapor:</Text>
        <TextInput 
          style={styles.transcriptBox}
          multiline
          value={transcript}
          onChangeText={setTranscript}
          placeholder="Mikrofonu açıp raporunuzu konuşarak dikte edin..."
          placeholderTextColor="#666"
        />
      </View>

      <View style={styles.barContainer}>
        {[...Array(5)].map((_, i) => {
          const animatedHeight = Math.max(10, audioLevel * 120 * (1 - (i % 3) * 0.15));
          return (
            <View
              key={i}
              style={[styles.bar, { height: isRecording ? animatedHeight : 10 }]}
            />
          );
        })}
      </View>

      <TouchableOpacity
        style={[styles.button, isRecording ? styles.btnStop : styles.btnStart]}
        onPress={isRecording ? stopRecording : startRecording}
      >
        <Text style={styles.btnText}>
          {isRecording ? 'Kaydı Bitir' : 'Dikte Et (Mikrofon)'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { alignItems: 'center', marginVertical: 20, width: '100%', paddingHorizontal: 20 },
  transcriptContainer: { width: '100%', marginBottom: 20 },
  label: { color: '#fff', fontSize: 16, marginBottom: 8, fontWeight: 'bold' },
  transcriptBox: { 
    backgroundColor: '#333', color: '#fff', minHeight: 80, padding: 10, 
    borderRadius: 8, textAlignVertical: 'top' 
  },
  barContainer: { flexDirection: 'row', alignItems: 'center', height: 80, gap: 8 },
  bar: { width: 8, borderRadius: 4, backgroundColor: '#10b981' },
  button: { padding: 12, borderRadius: 25, marginTop: 10 },
  btnStart: { backgroundColor: '#3b82f6' },
  btnStop: { backgroundColor: '#ef4444' },
  btnText: { color: '#fff', fontWeight: 'bold' },
});