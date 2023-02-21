# -*- coding: utf-8 -*-
"""TFlite_Python_Final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fNoNjYnVmDyvdPVTPykPDOMJkkbBhlyp
"""
import tflite_runtime.interpreter as tflite
import numpy as np
import scipy as sp
# !pip install spafe==0.2.0
import json
import spafe  # make sure that the version of spafe installed is spafe==0.2.0
from scipy.stats import kurtosis, skew, mode, gstd, describe, iqr, gmean, hmean, variation, tstd, gstd, moment, entropy
from spafe.features.gfcc import gfcc
from flask import Flask, request, jsonify

# import librosa
# from librosa.util import fix_length

# path = 'C:/Users/mohda/Downloads/Recording_26_O_M.wav'  # Insert path of audio fetched from the app



app = Flask(__name__)


@app.route('/')
def home():
    return "Hello world"


@app.route('/predict', methods=['POST'])
def predict():
    # y, sr = sf.read(path)
    data = request.json
    data = json.dumps(data)
    json_dictionary = json.loads(data)
    y = json_dictionary['y']
    sr = json_dictionary['sr']
    # y = y.tolist()
    y = np.array(y)
    # return y
    y = np.reshape(y, [66150,])
    # # y = np.array(y)
    # # return jsonify(y)
    # # y = np.reshape(y, [66150,])
    # sr = request.form.get('sr')
    # sr = int(sr)
    #
    required_audio_size = 3
    # padded_signal = fix_length(y, size=required_audio_size*sr)
    padded_signal = y

    Matrix = gfcc(sig=padded_signal, fs=sr, num_ceps=40, nfilts=128, nfft=2048, win_hop=0.0232, win_len=0.0464)
    Matrix = np.reshape(Matrix, [-1, 128, 40])
    Matrix = np.float32(Matrix)
    ft = sp.fft.fft(y)
    magnitude = np.absolute(ft)
    hist = magnitude[0:11025]
    k = kurtosis(hist)
    s = skew(hist)
    mean = np.mean(hist)
    z = np.array(mode(hist)[0])
    mode_var = float(z)
    i = iqr(hist)
    g = gmean(hist)
    h = hmean(hist)
    x = np.array(hist)
    dev = np.median(abs(x - np.median(x)))
    # dev=median_abs_deviation(hist)
    var = variation(hist)
    variance = np.var(hist)
    std = tstd(hist)
    gstd_var = gstd(hist)
    ent = entropy(hist)

    features = [mode_var, k, s, mean, i, g, h, dev, var, variance, std, gstd_var, ent]
    vector = np.array(features)
    b = np.linalg.norm(vector)
    vector = vector / b
    # vector=normalize([vector])
    vector = np.reshape(vector, [-1, 13])
    vector = np.float32(vector)

    interpreter = tflite.Interpreter(model_path='model2.tflite')
    interpreter.allocate_tensors()

    # Get input and output tensors
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    # Do predictions using the loaded TFLite model
    input_data_1 = Matrix  # Prepare your matrix input data
    input_data_2 = vector  # Prepare your vector input data
    interpreter.set_tensor(input_details[0]['index'], input_data_1)
    interpreter.set_tensor(input_details[1]['index'], input_data_2)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])

    predict1 = output_data
    predict = (predict1 > 0.5).astype("int32")
    confidence = predict1

    if predict[0][0] == 1:
        return jsonify({'vehicle': str(f"It is a car Probability: {confidence[0][0] * 100}%")})
        # print("It is a car")
        # print("confidence is ", confidence[0][0] * 100, "%")
    elif predict[0][1] == 1:
        return jsonify({'vehicle': str(f"It is a motorbike Probability: {confidence[0][1] * 100}%")})
        # print("It is a motorbike")
        # print("confidence is ", confidence[0][1] * 100, "%")
    elif predict[0][3] == 1:
        return jsonify({'vehicle': str(f"It is a truck Probability: {confidence[0][3] * 100}%")})
        # print("It is a truck")
        # print("confidence is ", confidence[0][3], "%")
    else:
        return jsonify({'vehicle': str(f"There is no vehicle in the audio Probability: {confidence[0][2] * 100}%")})
        # print("There is no vehicle in the audio")
    # return jsonify(y.tolist())


# print(predict())

if __name__ == '__main__':
    app.run(debug=True)
# {'C': 0, 'M': 1, 'N': 2, 'T': 3}
