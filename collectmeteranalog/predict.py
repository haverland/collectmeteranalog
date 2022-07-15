import tensorflow as tf
import numpy as np
import pkg_resources
import math

interpreter=None
internal_model_path = pkg_resources.resource_filename('collectmeteranalog', 'models/ana_i32s100_dropout.tflite')

def load_interpreter(model_path):
    global interpreter
    interpreter = tf.lite.Interpreter(model_path=model_path)
    return interpreter

def predict(image):
    global interpreter

    if interpreter==None:
        load_interpreter(internal_model_path)

    interpreter.allocate_tensors()
    input_index = interpreter.get_input_details()[0]["index"]
    input_shape = interpreter.get_input_details()[0]["shape"]
    
    output_index = interpreter.get_output_details()[0]["index"]

    image = image.resize((input_shape[2], input_shape[1]))
    
    interpreter.set_tensor(input_index, np.expand_dims(np.array(image).astype(np.float32), axis=0))
    # Run inference.
    interpreter.invoke()
    output = interpreter.get_tensor(output_index)
    if (len(output[0])==2):
        out_sin = output[0][0]  
        out_cos = output[0][1]
        return round(((np.arctan2(out_sin, out_cos)/(2*math.pi)) % 1) *10, 1)
    else:
        return round(np.argmax(output[0])/10,1)

    

        
    