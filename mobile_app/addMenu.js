import { useState, useEffect } from "react";
import { View, Text, FlatList, Pressable, StyleSheet, 
    Modal, TextInput, Image, ScrollView, Switch} from "react-native";
import * as ImagePicker from 'expo-image-picker';
import { useRoute } from '@react-navigation/native';
import Ionicons from '@expo/vector-icons/Ionicons';




export default function AddMenu(){
const [isVisible, setIsVisible] = useState(false)
const [menuItems, setMenuItems] = useState(false)
const [menuItemName, setMenuItemName] = useState('')
const [price, setPrice] = useState(0)
const [menuDescription, setMenuDescription] = useState('')
const [selectedImage, setSelectedImage] = useState(null)
const [availability, setAvailability] = useState({})
const [staple, setStaple] = useState([{}])
const route = useRoute();

const handlePriceChange = (text) => {
  const numericText = text.replace(/[^0-9]/g, '')
  setPrice(numericText === '' ? 0 : parseInt(numericText, 10))
}

const { token } = route.params || {};

useEffect(() => {
  fetchMenuItems();
  setMenuItems(true)
}, [token]);

async function fetchMenuItems(){
  try{     
    const response = await fetch('http://192.168.43.110:5000/api/menu/inventory', {
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

async function menuItemAvailability(itemId, isAvailable){
  try{     
    const response = await fetch(`http://192.168.43.110:5000/api/menu/toggle/${itemId}`, {
      method: "PATCH",
      headers:{
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        is_available: isAvailable
      })
    });
    
    const data = await response.json();
    setStaple(data); // Store response in staple state
    fetchMenuItems()
    console.log('Menu items:', data);
    
  } catch(error){
    console.log('fetch error:', error);
  }
}

    

    async function pushMenu(){
        try{ 
           /* const formData = new FormData();
            formData.append('name', menuItemName);
            formData.append('description', menuDescription);
            formData.append('price', price);
            if (selectedImage) {
                formData.append('image', {
                    uri: selectedImage.uri,
                    type: selectedImage.type || 'image/jpeg',
                    name: selectedImage.fileName || 'menu-image.jpg'
                });
            }*/
            
            await fetch('http://192.168.43.110:5000/api/menu/add',  {
                method: "POST",
                headers:{
                    'Authorization': `Bearer ${token}`,
                    'Content-Type' : 'application/json'
                },
                body: JSON.stringify({
                    name: menuItemName,
                    description: menuDescription,
                    price: price,
                    picture_url: selectedImage.uri
                })

                }).then(response => {
                    return response
                }).then( response => {
                    console.log(response);
                    console.log(selectedImage.uri)
                    setMenuItems(true)
                    fetchMenuItems()
                })
          }catch(error){
            console.log('fetch error:', error)
          }
       
    }



    const pickImage = async () => {

        const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();

        if (!permissionResult.granted) {
        Alert.alert('Permission required', 'Permission to access the media library is required.');
        return;
        }

        let result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ['images'],
        allowsEditing: true,
        aspect: [4, 3],
        quality: 1,
        });

        if (!result.canceled) {
        setSelectedImage(result.assets[0]);
        }
    }

   

    return(
       
        <View style={{margin: 10, flex: 1}}>
            {
              menuItems === false && (
                <View 
                    style={{
                       alignSelf: 'center',
                    }}
                >
                     <Pressable
                        onPress={()=>{setIsVisible(true)}}
                        style={{borderWidth: 1, width: 200, borderStyle: 'dashed',
                        marginTop: 10, height: 60, 
                        display: 'flex',
                        justifyContent: 'center',
                        borderRadius: 5
                        }}
                    >
                        <Text style={{alignSelf: 'center'}}>
                            Add new menu
                        </Text>
                    </Pressable>

                    <Modal
                      visible={isVisible}
                      animationType='slide'
                      transparent={false}
                      onRequestClose={()=>{setIsVisible(false)}}
                    >
                       <ScrollView style={{margin: 10,}}>
                         
                         {selectedImage && selectedImage.uri && <Image source={{ uri: selectedImage.uri }} 
                         style={styles.image} />}

                         <View style={styles.imageButton}>
                         <Pressable
                            onPress={pickImage}
                            style={{
                                height: 200, width: 200, borderWidth: 2, 
                                borderRadius: 5, display: selectedImage ? 'none':'flex',
                                alignItems: 'center', justifyContent: 'center',
                                borderStyle: 'dashed'
                            }}
                         >
                            <View>
                                <Ionicons name="images-outline" color="black" size={40}
                                style={{alignSelf: 'center'}} />
                                <Text>
                                    Place image
                                </Text>
                            </View>
                         </Pressable>

                          <Pressable
                            onPress={() => {setSelectedImage('')}}
                            style={{
                                height: 50, width: 100, borderWidth: 1, 
                                borderRadius: 5, display:selectedImage ? 'flex' : 'none', flexDirection: 'row',
                                justifyContent: 'center', 
                                
                            }}
                         >
                                <Text style={{alignSelf: 'center'}}>
                                    Delete image
                                </Text>
                         </Pressable>
                         </View>

                    
                        <View style={{
                            display:'flex', gap: 10,
                            marginTop: 10
                        }}>
                         <Text>
                            Name
                         </Text>

                         <TextInput
                            value={menuItemName}
                            onChangeText={setMenuItemName}
                            placeholder="Menu Item"
                            style={{borderWidth: 1, borderRadius: 5}}
                         />

                         <Text>
                            Price
                         </Text>

                         <TextInput
                            value={price.toString()}
                            onChangeText={handlePriceChange}
                            placeholder="Price"
                            keyboardType="number-pad"
                            style={{borderWidth: 1, borderRadius: 5}}
                         />

                         <Text>
                            Description
                         </Text>

                         <TextInput
                            value={menuDescription}
                            onChangeText={setMenuDescription}
                            placeholder="description"
                            style={{borderWidth: 1, borderRadius: 5}}
                         />

                         <Pressable
                            onPress={pushMenu}
                            style={{
                                backgroundColor: 'black', 
                                alignItems: 'center',
                                padding: 10, 
                                borderRadius: 5, width: 200, height: 40,
                                alignSelf: 'center', marginTop: 20
                            }}
                         >
                            <Text style={{color: 'white'}}>
                                Submit
                            </Text>
                         </Pressable>

                         </View>

                       </ScrollView>
                    </Modal>
                </View>
              )
            }

            {
                menuItems && (
                    <View style={{display: 'flex'}}>
                       <Text style={{fontWeight: 'bold', fontSize: 20}}>
                         Staple
                       </Text>

                       <FlatList
                          data={staple}
                          keyExtractor={(item, index) => item._id?.toString() || index.toString()}
                          renderItem={({item}) => (
                            <View style={{
                                display: 'flex', flexDirection: 'row', justifyContent: 'space-between',
                                alignItems: 'center', borderBottomWidth: 1
                            }}>
                                <Text>
                                    {item.name}
                                </Text>

                                <Text>
                                    {item.description}
                                </Text>

                                <View style={{display: 'flex', flexDirection:'row',
                                    alignItems:'center', gap: 10
                                }}>
                                    <Text>
                                        {item.is_available ? 'Available':'Unavailable'}
                                    </Text>

                                    <Switch
                                        trackColor={{false: '#767577', true: '#f5c646'}}
                                        onValueChange={(newValue) => menuItemAvailability(item._id || item.id, newValue)}
                                        value={item.is_available}
                                    />
                                </View>

                                
                            </View>
                )}
                       
                       />
                    <View style={{display: 'flex', alignItems: 'center'}}>
                       <Pressable
                        onPress={()=>{setIsVisible(true)}}
                        style={{borderWidth: 1, width: 200, borderStyle: 'dashed',
                        marginTop: 10, height: 60, 
                        display: 'flex',
                        justifyContent: 'center',
                        borderRadius: 5
                        }}
                    >
                        <Text style={{alignSelf: 'center', fontWeight: 'bold'}}>
                            Add new menu
                        </Text>
                    </Pressable>
                    </View>

                    <Modal
                      visible={isVisible}
                      animationType='slide'
                      transparent={false}
                      onRequestClose={()=>{setIsVisible(false)}}
                    >
                       <ScrollView style={{margin: 10, marginTop: 50}}>
                         
                         {selectedImage && selectedImage.uri && <Image source={{ uri: selectedImage.uri }} 
                         style={styles.image} />}

                         <View style={styles.imageButton}>
                         <Pressable
                            onPress={pickImage}
                            style={{
                                height: 200, width: 200, borderWidth: 2, 
                                borderRadius: 5, display: selectedImage ? 'none':'flex',
                                alignItems: 'center', justifyContent: 'center',
                                borderStyle: 'dashed'
                            }}
                         >
                            <View>
                                <Ionicons name="images-outline" color="#f5c646" size={40}
                                style={{alignSelf: 'center'}} />
                                <Text style={{fontWeight: 'bold'}}>
                                    Place image
                                </Text>
                            </View>
                         </Pressable>

                          <Pressable
                            onPress={() => {setSelectedImage('')}}
                            style={{
                                height: 50, width: 100, borderWidth: 1, 
                                borderRadius: 5, display:selectedImage ? 'flex' : 'none', flexDirection: 'row',
                                justifyContent: 'center', marginTop: 10
                            }}
                         >
                                <Text style={{alignSelf: 'center', fontWeight: 'bold'}}>
                                    Delete image
                                </Text>
                         </Pressable>
                         </View>

                    
                        <View style={{
                            display:'flex', gap: 10,
                            marginTop: 10
                        }}>
                         <Text>
                            Name
                         </Text>

                         <TextInput
                            value={menuItemName}
                            onChangeText={setMenuItemName}
                            placeholder="Menu Item"
                            style={{borderWidth: 1, borderRadius: 5}}
                         />

                         <Text>
                            Price
                         </Text>

                         <TextInput
                            value={price.toString()}
                            onChangeText={handlePriceChange}
                            placeholder="Price"
                            keyboardType="number-pad"
                            style={{borderWidth: 1, borderRadius: 5}}
                         />

                         <Text>
                            Description
                         </Text>

                         <TextInput
                            value={menuDescription}
                            onChangeText={setMenuDescription}
                            placeholder="description"
                            style={{borderWidth: 1, borderRadius: 5}}
                         />

                         <Pressable
                            onPress={pushMenu}
                            style={{
                                backgroundColor: '#f5c646', 
                                alignItems: 'center',
                                padding: 10, 
                                borderRadius: 5, width: 200, height: 40,
                                alignSelf: 'center', marginTop: 20
                            }}
                         >
                            <Text style={{color: 'white'}}>
                                Submit
                            </Text>
                         </Pressable>

                         </View>

                       </ScrollView>
                    </Modal>
                    </View>
                )
            }

           

          
        </View>
        
    )
}

const styles = StyleSheet.create({
    image:{
        height: 200,
        width: 200,
        alignSelf: 'center',
        borderRadius: 10,
        zIndex: 1
    },
    imageButton:{
        display: 'flex',
        alignItems: 'center',
        gap: 10
    }
})