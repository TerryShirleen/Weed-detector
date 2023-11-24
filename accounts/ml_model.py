# ml_model.py
#import joblib
#import os
# ml_model.py
#import joblib

#def load_pickled_model():
    # Load the pickled model
    #return joblib.load('http://localhost:8888/edit/Desktop/Weed_CNN/models/weedcropcnn.pkl')

# ml_model.py
import joblib
import os

#def load_pickled_model():
    # Assuming the pickle file is in the 'models' directory
    #model_path = os.path.join('Weed_Detector', 'models', 'weedcropcnn.pkl')
    #return joblib.load(model_path)


# ml_model.py
import joblib
import os
import numpy as np

def load_pickled_model():
    # Assuming the pickle file is in the 'models' directory
    model_path = os.path.join('accounts', 'Weed_CNN', 'weedcropcnn.pkl')
    return joblib.load(model_path)

def make_prediction(model, input_data):
    # Assuming your model.predict method is suitable for your use case
    predictions = model.predict(input_data)
    return predictions

