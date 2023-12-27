from roboflow import Roboflow
import streamlit as st

with open('RoboflowKey.txt', 'r') as f:
    key = f.read()

# Create a dictionary to map product names based on the values from the prediction
product_mapping = mapping = {
    '15': "Corn",
    '16': "Zucchini",
    '17': "Eggplant",
    '18': "Eggs",
    '19': "Fish",
    '20': "Musk Melon",
    '21': "Grapes",
    '22': "Honey Dew Melon",
    '23': "Juice",
    '24': "Cabbage",
    '25': "Meat",
    '26': "Milk",
    '28': "Mushroom",
    '29': "Nectarine",
    '30': "Lime",
    '31': "Orange",
    '32': "Kiwi",
    '33': "Mango",
    '35': "Red Berries",
    '36': "Leafy Vegetables",
    '37': "Dressings",
    '38': "Spinach",
    '39': "Bottle Gourd",
    '40': "Strawberry",
    '42': "Tofu",
    '43': "Tomato",
    '44': "Water Melon",
    '45': "Yoghurt",
    'black-olives': "black-olives",
    'canned-black-beans': "canned-black-beans",
    'canned-black-olives': "canned-black-olives",
    'canned-kidney-beans': "canned-kidney-beans",
    'canned-peaches': "canned-peaches",
    'canned-tomatoes': "canned-tomatoes",
    'condensed-milk': "condensed-milk",
    'evaporate-milk': "evaporate-milk",
    'fried-onion': "fried-onion",
    'kidney-beans': "kidney-beans",
    'marinara-sauce': "marinara-sauce",
    'pasta-sauce': "pasta-sauce",
    'spaghetti-sauce': "spaghetti-sauce",
    'tomato-paste': "tomato-paste",
    'tomato-sauce': "tomato-sauce",
}

def map_product_name(value):
    value = str(value)
    # Map the product name based on the provided value
    return product_mapping.get(value, f"{value}")

def predict(image_path):
    rf = Roboflow(api_key=key)
    project = rf.workspace().project(
        "items-grocery-detect")
    model = project.version(1).model
    prediction = model.predict(image_path, confidence=40, overlap=30).json()
#    st.write(prediction)

    # Process the prediction results and map product names
    for item in prediction["predictions"]:
        class_value = item["class"]
        item["mapped_product_name"] = map_product_name(class_value)
        #st.write(item["mapped_product_name"])

    # st.write(prediction)
    model.predict(image_path, confidence=40, overlap=30).save(
        "savedprediction.jpg")
    st.image('savedprediction.jpg',
             caption="Annotated Image", use_column_width=True)

    return prediction
