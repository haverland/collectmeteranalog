import numpy as np
import pkg_resources
import math

has_tflite_runtime = False
model_path = None
interpreter = None


def load_interpreter(path):
    global has_tflite_runtime, interpreter, model_path

    model_path = path

    if (model_path==None or model_path=="off"):
        print("Prediction by model disabled: No model selected")
        return -1
    
    # Import tensorflow libraries
    try:
        import tflite_runtime.interpreter as tflite
        has_tflite_runtime = True
    except ImportError:
        try:
            import tensorflow.lite as tflite
            has_tflite_runtime = True
        except ImportError:
            has_tflite_runtime = False
            print("Prediction by model disabled: tensorflow or tflite-runtime package missing")
            return -1

    # Init tensorflow
    try:
        print("Selected model file: " + model_path)
        interpreter = tflite.Interpreter(model_path=model_path)
        interpreter.allocate_tensors()
    except Exception as e:
        print(f"Prediction by model disabled. Error: {e}")
        return

    # Identify model type
    try:
        input_details = interpreter.get_input_details()
        input_shape = input_details[0]['shape']
        dummy_input = np.zeros(input_shape, dtype=np.float32) # Dummy data

        interpreter.set_tensor(input_details[0]['index'], dummy_input)
        interpreter.invoke()

        output_index = interpreter.get_output_details()[0]["index"]
        output = interpreter.get_tensor(output_index)

        if len(output[0]) == 2:
            print("Prediction by model enabled. Model type: ana-cont")
        elif len(output[0]) == 100:
            print("Prediction by model enabled. Model type: ana-class100")
        else:
            print(f"Model type not supported. Detected classes: {len(output[0])}")
            interpreter = None

    except Exception as e:
        print(f"Error during model type detection: {e}")
        interpreter = None
    

def predict(image):
    if (model_path == None or model_path == "off" or has_tflite_runtime == False or interpreter == None):
        #print("Prediction disabled")
        return -1
    
    input_index = interpreter.get_input_details()[0]["index"]
    input_shape = interpreter.get_input_details()[0]["shape"]
    output_index = interpreter.get_output_details()[0]["index"]

    image = image.resize((input_shape[2], input_shape[1]))

    interpreter.set_tensor(input_index, np.expand_dims(np.array(image).astype(np.float32), axis=0))
    interpreter.invoke() # Run inference.
    output = interpreter.get_tensor(output_index)
    
    if (len(output[0])==2):
        out_sin = output[0][0]  
        out_cos = output[0][1]
        prediction = round(((np.arctan2(out_sin, out_cos)/(2*math.pi)) % 1) *10, 1)
    
    elif (len(output[0])==100):
        prediction = (np.argmax(output, axis=1).reshape(-1)/10)[0]
    else:
        print(f"Model type not supported. Detected classes: {len(output[0])}")
        prediction = -1
        
    return prediction
 