import { StyleSheet, View, Text } from "react-native";

export default function Transactions(){
    return (
        <View style={{margin: 10}}>
            <Text style={{fontWeight: 'bold', fontSize: 20}}>
                Today's transactions
            </Text>

            <View style={{display: 'flex', flexDirection: 'row',
                 backgroundColor: '#C6D4FF', margin: 10,
                 borderRadius: 5, elevation: 5, justifyContent: 'flex-start'
                 }}>
                <View style={{borderRightWidth: 1}}>
                    <Text style={{margin: 5}}>
                        Date
                    </Text>
                </View>

                <View style={{borderRightWidth: 1}}>
                    <Text style={{margin: 5}}>
                        Name
                    </Text>
                </View>

                <View style={{borderRightWidth: 1}}>
                    <Text style={{margin: 5}}>
                        Meal 
                    </Text>
                </View>

                <View>
                    <Text style={{margin: 5}}>
                        Time
                    </Text>
                </View>
            </View>
        </View>
    )
}