import { StatusBar } from 'expo-status-bar';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StyleSheet, Text, View, Image, Pressable} from 'react-native';
import { useEffect, useState } from 'react';

export default function QrCodeGen({ route }){
  const { qrCode } = route.params || {};
  const { mealToken } = route.params || {};
  const [mealQrCode, setMealQrCode] = useState(null);
  
    return (
        <SafeAreaView style={{ flex: 1, margin: 10 }}>
             <View style={styles.heading}>
              <View style={{flex: 1, flexDirection: 'row', justifyContent: 'center'}}>
                <Text style={{ fontWeight: 'bold', fontSize: 20 }}>
                Here is your Order
                </Text>
                <StatusBar style="auto" />
              </View>
               
               <View style={styles.qr}>
                    <Image source={{ uri: `http://192.168.43.110:2000/${qrCode}`}} style={{ width: 250, height: 250 }} />
                    <Text>{mealToken}</Text>
               </View>
             </View>
            
        </SafeAreaView>
    )}

const styles = StyleSheet.create({
 heading:{
    flex: 1, 
    flexDirection: 'column'
  },
  qr:{
    flex: 3,
    alignSelf: 'center'
  }
})