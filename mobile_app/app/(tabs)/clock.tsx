import { useState } from "react";
import { View, Text, Button, Alert } from "react-native";
import * as Location from "expo-location";
import { mobileAPI } from "../../src/api/client";
import { distanceMeters } from "../../src/utils/geo";
import { format } from "date-fns";

const STORE = { lat: 37.5665, lon: 126.9780, radius: 120 };

export default function Clock() {
  const [busy, setBusy] = useState(false);
  
  const clockIn = async () => {
    setBusy(true);
    try {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== "granted") throw new Error("위치 권한이 필요합니다.");
      const pos = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
      const d = distanceMeters(pos.coords.latitude, pos.coords.longitude, STORE.lat, STORE.lon);
      if (d > STORE.radius) throw new Error(`출근 가능 반경 초과 (${Math.round(d)}m)`);
      
      const result = await mobileAPI.clockIn({ 
        lat: pos.coords.latitude, 
        lng: pos.coords.longitude
      });
      Alert.alert("출근 완료", format(new Date(result.at), "yyyy-MM-dd HH:mm"));
    } catch (e:any) { 
      Alert.alert("실패", e.message ?? "출근 처리 오류"); 
    } finally { 
      setBusy(false); 
    }
  };
  
  const clockOut = async () => {
    setBusy(true);
    try {
      const result = await mobileAPI.clockOut({});
      Alert.alert("퇴근 완료", format(new Date(result.at), "yyyy-MM-dd HH:mm"));
    } catch (e:any) { 
      Alert.alert("실패", e.message ?? "퇴근 처리 오류"); 
    } finally { 
      setBusy(false); 
    }
  };
  
  return (
    <View style={{ padding: 16, gap: 12 }}>
      <Text style={{ fontSize: 18, fontWeight: "600" }}>출/퇴근</Text>
      <Button title={busy ? "처리 중..." : "출근"} onPress={clockIn} disabled={busy}/>
      <Button title={busy ? "처리 중..." : "퇴근"} onPress={clockOut} disabled={busy}/>
    </View>
  );
}
