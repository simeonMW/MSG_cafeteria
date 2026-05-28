import { StyleSheet, View, Text, Pressable } from 'react-native';
import { CameraView, useCameraPermissions } from 'expo-camera';
import { useState } from 'react';
import Entypo from '@expo/vector-icons/Entypo';


export default function ChefPage() {

    const [permission, requestPermission] = useCameraPermissions();
    const [cameraActive, setCameraActive] = useState(false);

    const handleScan = ({ data }) => {
        // Handle the scanned QR code data here

        console.log('Scanned QR code:', data);
        setCameraActive(false); // Close camera after scanning
    };

    if (!permission) {
        return (
            <View style={styles.scanner}>
                <Pressable
                    onPress={() => {
                        requestPermission();
                        setCameraActive(true);
                    }}
                    style={styles.scanButton}
                >
                    <Entypo name="camera" size={40} color='#f5c646' style={{alignSelf: 'center'}}/>
                    <Text style={{ 
                    fontSize: 20, alignSelf: 'center'}}>
                        Confirm Order
                    </Text>
                </Pressable>
            </View>
        );
    }

    if (!permission.granted) {
        return (
            <View style={styles.scanner}>
                <Text>Camera permission is required to scan QR codes.</Text>
                <Pressable onPress={requestPermission}>
                    <Text>Grant Permission</Text>
                </Pressable>
            </View>
        );
    }

    return (
        <View style={styles.container}>
            {cameraActive ? (
                <View style={styles.cameraContainer}>
                    <CameraView 
                        style={styles.camera}
                        barcodeScannerSettings={{
                            barcodeTypes: ['qr']
                        }}
                        onBarcodeScanned={handleScan}
                    />
                    <Pressable 
                        style={styles.closeButton}
                        onPress={() => setCameraActive(false)}
                    >
                        <Text style={styles.closeButtonText}>Close</Text>
                    </Pressable>
                </View>
            ) : (
                <View style={styles.scanner}>
                    <Pressable
                        onPress={() => setCameraActive(true)}
                        style={styles.scanButton}
                    >
                        <Entypo name="camera" size={40} color='#f5c646' style={{alignSelf: 'center'}}/>
                        <Text style={{ 
                        fontSize: 20, alignSelf: 'center',
                        fontWeight: 'bold'
                        }}>
                            Confirm Order
                        </Text>
                    </Pressable>
                </View>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    scanner:{
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center'
    },

    scanButton: {
        display: 'flex',
        justifyContent: 'center', 
        width: 300, 
        height: 300, 
        borderWidth: 2,
        borderStyle: 'dashed',
        borderRadius: 10
    },
    cameraContainer: {
        flex: 1,
        flexDirection: 'row',
        justifyContent: 'center', 
    },
    camera: {
        width: 300,
        height: 300,
        alignSelf: 'center',
        overflow: 'hidden',
        borderRadius: 30
    },
    closeButton: {
        position: 'absolute',
        top: 50,
        right: 20,
        backgroundColor: 'rgba(0,0,0,0.5)',
        padding: 10,
        borderRadius: 5,
    },
    closeButtonText: {
        color: 'white',
        fontSize: 16,
    }
})