import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { useGLTF, OrbitControls } from '@react-three/drei';
import { ActivityIndicator, View } from 'react-native';

function MyAvatar() {
  // public klasöründen modeli çekiyoruz
  const { scene } = useGLTF('/avatar.glb');
  
  return <primitive object={scene} scale={2} position={[0, -2, 0]} />;
}

// Model yüklenirken ekranda dönecek yükleme animasyonu
function Loader() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <ActivityIndicator size="large" color="#10b981" />
    </View>
  );
}

export default function AvatarScene() {
  return (
    <Suspense fallback={<Loader />}>
      <Canvas camera={{ position: [0, 0, 5], fov: 50 }}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[10, 10, 10]} intensity={1} />
        
        <MyAvatar />
        
        <OrbitControls enableZoom={false} />
      </Canvas>
    </Suspense>
  );
}