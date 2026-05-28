import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { StyleSheet, Text, View, Image, 
  Pressable, TextInput, FlatList, KeyboardAvoidingView, Platform} from 'react-native';
import { useState, useEffect } from 'react';
import { NavigationContainer, useNavigation } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import QrCodeGen from './qrCodePage';
const nsimaImage = require('./assets/nsima.png')
const riceImage = require('./assets/rice.png')
const chipsImage = require('./assets/chips.png')
const mincedImage = require('./assets/minced.png')
const chickenImage = require('./assets/chicken.png')
const beefImage = require('./assets/beef.png')
import MaterialCommunityIcons from '@expo/vector-icons/MaterialCommunityIcons';
import Ionicons from '@expo/vector-icons/Ionicons';
import FontAwesome from '@expo/vector-icons/FontAwesome';
import ChefPage from './chefHomeScreen';
import AddMenu from './addMenu';
import Transactions from './transactions';




const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function Register({ navigation, setIsLoggedIn, setUserRole }){

  const [password, setPassword] = useState('');
  const [userName, setUserName] = useState('');
  const [userId, setUserId] = useState('')
  const [token, setToken] = useState('')
  

 /*const loggedIn = (data) => {
    
      setIsLoggedIn(true);
      setToken(data.token);
      
      // Navigate to the appropriate screen based on user role
      if (data.user.email === userName.toLowerCase()  && userId === data.user.employee_number) {
        setUserRole('customer');
        navigation.navigate('CustomerApp', { token: data.token });
      } else if (data.user.role === 'chef') {
        setUserRole('chef');
        navigation.navigate('ChefApp', { token: data.token });
      }
    
  }*/

  const loggedIn = () => {
    
      setIsLoggedIn(true);
      // Navigate to the appropriate screen based on user role
      if ( userName.toLowerCase() === 'customer'  && userId ) {
        setUserRole('customer');
        navigation.navigate('CustomerApp');
      } else if (userName === 'chef') {
        setUserRole('chef');
        navigation.navigate('ChefApp');
      }
    
  }

  async function login(){
    try{
      await fetch('http://192.168.43.110:5000/api/auth/login', 
        {
          method: "POST",
          headers:{
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: userName,
            password: password, 
            employee_number: userId
          })

        }
      )
      .then((response) => {
        return response.json()
      })
      .then( response => {
        console.log(response)
        loggedIn(response)
      }
      )
    }catch(error){
      console.log("fetch error:",error);
    }
  } 
  
  return(
    <View style={styles.login}>
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"}>
      <View >
        <View style={{marginTop: 50, marginBottom: 100}}>
          <Text style={{alignSelf: 'center', 
            fontWeight: 'bold', 
            fontSize: 20}}>
            Sign up
          </Text>

          <Text style={{alignSelf: 'center'}}>
            Please register your credentials below
          </Text>
        </View>
      

      <View style={{display: 'flex', gap: 15}}>

        <View style={{display: 'flex', gap: 5}}>
          <View style={{flexDirection: 'row', alignItems: 'center', gap: 5}}>
              <Ionicons name="person-outline" size={20} color="#f5c646"/>
              <Text>
              Username
              </Text>
          </View>

          <TextInput
          value={userName}
          onChangeText={setUserName}
          keyboardType='email-address'
          placeholder='Username'
          style={{borderWidth: 1, borderRadius: 5}}
        />
        </View>
        
      <View style={{display: 'flex', gap: 5}}>
        <View style={{flexDirection: 'row', alignItems: 'center', gap: 5}}>
          <Ionicons name="lock-closed-outline" size={20} color="#f5c646"/>
          <Text>
            Password
          </Text>
        </View>

        <TextInput
        value={password}
        onChangeText={setPassword}
        placeholder='Password'
        style={{borderWidth: 1, borderRadius: 5}}
      />
      </View>
      

      <View style={{display: 'flex', gap: 5}}>
        <View style={{flexDirection: 'row', alignItems: 'center', gap: 5}}>
          <Ionicons name="card-outline" size={20} color="#f5c646"/>
          <Text>
              Employement Number
          </Text>
        </View>

          <TextInput
          value={userId}
          onChangeText={setUserId}
          placeholder='Employement Number'
          style={{borderWidth: 1, borderRadius: 5}}
        />
        </View>
      </View>

      <Pressable
        onPress={loggedIn}
        style={{backgroundColor: userName && password ? '#f5c646' : '#f4d16fc0',
          width: 200, alignSelf: 'center', height: 40, borderRadius: 5,
          display: 'flex', justifyContent: 'center', marginTop: 50
        }}
      >
        <Text style={{alignSelf: 'center', color: 'white'}}>
          Sign up 
        </Text>
      </Pressable>

      <View style={{display: 'flex', flexDirection: 'row', gap: 5, justifyContent: 'center', marginTop: 20}}>
        <Text>
          Already have an account?
        </Text>

        <Pressable onPress={() => navigation.navigate('Login')}>
          <Text style={{color: '#ffc011'}}>
            Login instead
          </Text>
        </Pressable>
      </View>
      </View>
      </KeyboardAvoidingView>
      
    </View>
)
   
}


function Login({ navigation, setIsLoggedIn, setUserRole }){

  const [password, setPassword] = useState('');
  const [userName, setUserName] = useState('');
  const [userId, setUserId] = useState('')
  const [token, setToken] = useState('')
  

 /*const loggedIn = (data) => {
    
      setIsLoggedIn(true);
      setToken(data.token);
      
      // Navigate to the appropriate screen based on user role
      if (data.user.email === userName.toLowerCase()  && userId === data.user.employee_number) {
        setUserRole('customer');
        navigation.navigate('CustomerApp', { token: data.token });
      } else if (data.user.role === 'chef') {
        setUserRole('chef');
        navigation.navigate('ChefApp', { token: data.token });
      }
    
  }*/

  const loggedIn = () => {
    
      setIsLoggedIn(true);
      // Navigate to the appropriate screen based on user role
      if ( userName.toLowerCase() === 'customer'  && userId ) {
        setUserRole('customer');
        navigation.navigate('CustomerApp');
      } else if (userName === 'chef') {
        setUserRole('chef');
        navigation.navigate('ChefApp');
      }
    
  }

  async function login(){
    try{
      await fetch('http://192.168.43.110:5000/api/auth/login', 
        {
          method: "POST",
          headers:{
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: userName,
            password: password, 
            employee_number: userId
          })

        }
      )
      .then((response) => {
        return response.json()
      })
      .then( response => {
        console.log(response)
        loggedIn(response)
      }
      )
    }catch(error){
      console.log("fetch error:",error);
    }
  } 
  
  return(
    <View style={styles.login}>
      <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"}>
      <View >
        <View style={{marginTop: 50, marginBottom: 100}}>
          <Text style={{alignSelf: 'center', 
            fontWeight: 'bold', 
            fontSize: 20}}>
            Login
          </Text>

          <Text style={{alignSelf: 'center'}}>
            Please enter your credentials below
          </Text>
        </View>
      

      <View style={{display: 'flex', gap: 15}}>

        <View style={{display: 'flex', gap: 5}}>
          <View style={{flexDirection: 'row', alignItems: 'center', gap: 5}}>
              <Ionicons name="person-outline" size={20} color="#f5c646"/>
              <Text>
              Username
              </Text>
          </View>

          <TextInput
          value={userName}
          onChangeText={setUserName}
          keyboardType='email-address'
          placeholder='Username'
          style={{borderWidth: 1, borderRadius: 5}}
        />
        </View>
        
      <View style={{display: 'flex', gap: 5}}>
        <View style={{flexDirection: 'row', alignItems: 'center', gap: 5}}>
          <Ionicons name="lock-closed-outline" size={20} color="#f5c646"/>
          <Text>
            Password
          </Text>
        </View>

        <TextInput
        value={password}
        onChangeText={setPassword}
        placeholder='Password'
        style={{borderWidth: 1, borderRadius: 5}}
      />

      <Pressable>
        <Text style={{color: '#c7a33f'}}>
          Forgot password?
        </Text>
      </Pressable>
      </View>
      

      <View style={{display: 'flex', gap: 5}}>
        <View style={{flexDirection: 'row', alignItems: 'center', gap: 5}}>
          <Ionicons name="card-outline" size={20} color="#f5c646"/>
          <Text>
              Employement Number
          </Text>
        </View>

          <TextInput
          value={userId}
          onChangeText={setUserId}
          placeholder='Employement Number'
          style={{borderWidth: 1, borderRadius: 5}}
        />
        </View>
      </View>

      <Pressable
        onPress={loggedIn}
        style={{backgroundColor: userName && password ? '#f5c646' : '#f4d16fc0',
          width: 200, alignSelf: 'center', height: 40, borderRadius: 5,
          display: 'flex', justifyContent: 'center', marginTop: 50
        }}
      >
        <Text style={{alignSelf: 'center', color: 'white'}}>
          Login 
        </Text>
      </Pressable>

      <View style={{display: 'flex', flexDirection: 'row', gap: 5, justifyContent: 'center', marginTop: 20}}>
        <Text>
          Don't have an account?
        </Text>

        <Pressable onPress={() => navigation.navigate('Register')}>
          <Text style={{color: '#ffc011'}}>
            Create account
          </Text>
        </Pressable>
      </View>
      </View>
      </KeyboardAvoidingView>
      
    </View>
)
   
}

function MenuScreen({ route }) {
  const { token } = route.params || {};
  const navigation = useNavigation();
  const [buttonColor, setButtonColor] = useState('breakfast');
  const [stapleButton, setStapleButton] = useState('');
  const [selectedStapleId, setSelectedStapleId] = useState(null);
  const [proteinButton, setProteinButton] = useState('');
  const [qrCode, setQrCode] = useState()
  const [mealToken, setMealToken] = useState()


  const [staple, setStaple] = useState([{}])

  const protein = [
      {
        id: 1,
        name: 'Chicken',
        image: chickenImage
      },
      {
       id: 2,
       name: "Beef", 
       image: beefImage
      },
      {
        id: 3,
        name: "Minced meat",
        image: mincedImage
      }
      
    ]

    useEffect(() => {
      if (token) {
        fetchMenuItems();
      }
    }, [token]);
    
    async function fetchMenuItems(){
      try{     
        const response = await fetch('http://192.168.43.110:5000/api/menu/public', {
          method: "GET",
          headers:{
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        setStaple(data); // Store response in staple state
        console.log('Menu items:', data);
        
      } catch(error){
        console.log('fetch error:', error);
      }
    }

    async function pressOrder(){
      try{

        const response = await fetch('http://192.168.43.110:5000/api/orders/place', {
          method: "POST",
          headers:{
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            item_id: selectedStapleId
          })
        });

        const data = await response.json();
        console.log('Order response:', data);
        const normalizedQrCode = data.qr_code_url?.match(/([^\\/]+\.png)$/)?.[1];
        setQrCode(normalizedQrCode)
        setMealToken(data.token)


      } catch(error){
        console.log('fetch error:', error);
        return null;
      }
    }

  return (
      <SafeAreaView style={{ display: 'flex', margin: 10 }}>
        <View style={styles.topBanner}>

          <View style={styles.staple}>
            <Text style={{fontWeight: 'bold', fontSize: 20, paddingBottom:5}}>Staple</Text>
            
            <FlatList
              key="staple-grid"
              data={staple}
              numColumns={3}
              keyExtractor={(item, index) => item._id?.toString() || index.toString()}
              renderItem={({item}) => (
                <View>
                <Pressable 
                  onPress={() => {
                    if (stapleButton === item.name) {
                      setStapleButton('')
                      setSelectedStapleId(null)
                    } else {
                      setStapleButton(item.name)
                      setSelectedStapleId(item._id || item.id)
                    }
                  }}
                  style={{backgroundColor: stapleButton === item.name ? '#f5c646': 'white', 
                  padding: 10, height: 150, borderRadius: 10, width: 120,
                  marginRight: 10, elevation: 5
                  }}
                >
                    <Image source={item.picture_url} style={{width: 100, borderRadius: 5}}/>
                    <Text style={{color: stapleButton=== item.name ? 'white': 'black'}}>
                      {item.name}
                      </Text>
                </Pressable>
              </View>
              )}/>
           
            
          </View>
          

           <View style={styles.protein}>
            <Text style={{fontWeight: 'bold', fontSize: 20, paddingBottom:5}}>protein</Text>
            
            <FlatList
              key="protein-grid"
              data={protein}
              numColumns={3}
              keyExtractor={(item) => item.id.toString()}
              renderItem={({item}) => (
                <View>
                <Pressable 
                  onPress={() => {
                    if (proteinButton === item.name) {
                      setProteinButton('')
                    } else {
                      setProteinButton(item.name)
                    }
                  }}
                  style={{backgroundColor: proteinButton === item.name ? '#f5c646': 'white', 
                  padding: 10, height: 150, borderRadius: 10,
                  marginRight: 10, elevation: 5
                  }}
                >
                    <Image source={item.image} style={{width: 100, borderRadius: 5}}/>
                    <Text style={{color: 'black'}}>
                      {item.name}
                      </Text>
                </Pressable>
              </View>
              )}
            />  
          </View>


          <View style={{flex: 1, flexDirection: 'row', justifyContent: 'center'}}>
            {stapleButton && proteinButton && (
              <Pressable
                onPress={() => {
                    pressOrder()
                    navigation.navigate('QR Code')
                    console.log(qrCode)
                }}
                style={{backgroundColor: 'black', alignItems: 'center',
                  padding: 10, borderRadius: 5, width: 200, height: 40  
                }}
              >
                <Text style={{color: 'white'}}>Press Order</Text>
              </Pressable>
            )}
          </View>
        </View>
      </SafeAreaView>
  );
}

// Customer Tab Navigator
function CustomerTabs({ route }) {
  const { token } = route.params || {};

  return (
    <Tab.Navigator>
      <Tab.Screen 
        name="Menu" 
        component={MenuScreen} 
        initialParams={{ token }}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="restaurant" color={color} size={size} />
          ), tabBarActiveTintColor: 'black'
        }}
      />
      <Tab.Screen 
        name="QR Code" 
        component={QrCodeGen} 
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="qr-code-outline" color={color} size={size} />
          ), tabBarActiveTintColor: 'black'
        }}
      />
    </Tab.Navigator>
  );
}

// Chef Tab Navigator
function ChefTabs({ route }) {
  const { token } = route.params || {};
  return (
    <Tab.Navigator>
      <Tab.Screen 
        name="scan code" 
        component={ChefPage} 
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="qr-code-outline" color={color} size={size} />
          ), tabBarActiveTintColor: '#FF8811'
        }}
      />
      <Tab.Screen 
        name="add menu" 
        component={AddMenu} 
        initialParams={{ token }}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="add-circle-outline" color={color} size={size} />
          ), tabBarActiveTintColor: '#FF8811'
        }}
      />
      <Tab.Screen
        name='menu'
        component={MenuScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="restaurant" color={color} size={size} />
          ), tabBarActiveTintColor: '#FF8811'
        }}
      />
      <Tab.Screen 
        name="Transactions" 
        component={Transactions} 
        options={{
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="receipt-outline" color={color} size={size} />
          ), tabBarActiveTintColor: '#FF8811'
        }}
      />
    </Tab.Navigator>
  );
}

// Main App with Stack Navigation
export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState('');

  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator 
          screenOptions={{ headerShown: false }}
          initialRouteName={isLoggedIn ? userRole === 'customer' ? 'CustomerApp' : 'ChefApp' : 'Register'}
        >
          <Stack.Screen name="Register">
            {props => <Register {...props} setIsLoggedIn={setIsLoggedIn} setUserRole={setUserRole} />}
          </Stack.Screen>
          <Stack.Screen name="Login">
            {props => <Login {...props} setIsLoggedIn={setIsLoggedIn} setUserRole={setUserRole} />}
          </Stack.Screen>
          <Stack.Screen name="CustomerApp" component={CustomerTabs} />
          <Stack.Screen name="ChefApp" component={ChefTabs} />
        </Stack.Navigator>
      </NavigationContainer>
      <StatusBar style="auto" />
    </SafeAreaProvider>
  );
}

const styles = StyleSheet.create({

  topBanner:{
    display: 'flex',
  },

  mealType:{
    display: 'flex',
    flexDirection: 'row',
    columnGap: 10,
  },

  staple:{
    display: 'flex', 
    marginBottom: 10
  },

  protein:{
    display: 'flex',
  },

  button: {
    backgroundColor: 'grey',
    width: 50
  },

  login:{
    flex: 1,
    justifyContent: 'flex-start', 
    gap: 20,
    margin: 20
    
  }
});
