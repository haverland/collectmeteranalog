import tensorflow as tf
import numpy as np
import pkg_resources
import math


def predict( image, model_path='ana0910s1_dropoutq.tflite'):
    DATA_PATH = pkg_resources.resource_filename('collectmeteranalog', 'models/' + model_path)

    interpreter = tf.lite.Interpreter(model_path=DATA_PATH)
    interpreter.allocate_tensors()
    input_index = interpreter.get_input_details()[0]["index"]
    output_index = interpreter.get_output_details()[0]["index"]

    interpreter.set_tensor(input_index, np.expand_dims(np.array(image).astype(np.float32), axis=0))
    # Run inference.
    interpreter.invoke()
    output = interpreter.get_tensor(output_index)
    out_sin = output[0][0]  
    out_cos = output[0][1]
    return round(((np.arctan2(out_sin, out_cos)/(2*math.pi)) % 1) *10, 1)

    

        
    