import pandas as pd 
import numpy as np 
import joblib 
import cv2

dimensions = (30, 30)

def predict(img, model):
    preds = model.predict_proba(img)
    return preds.reshape(5)

def run(img):

    img = cv2.resize(img, dimensions, interpolation = cv2.INTER_AREA)

    X = img[:, :, 0]

    X = X.reshape(1, 900)

    X = X.astype('float64')

    X = pd.DataFrame(X)

    d = {"downdog": 0, "goddess": 1, "plank": 2, "tree": 3, "warrior2": 4}
    d = {v: k for k, v in d.items()}

    preds = []

    for i in range(5):
        model = joblib.load(f"models/xgb_{i}.bin")
        temp = predict(X, model)

        if i == 0:
            preds = temp 
        else:
            preds = [i + j for i, j in zip(preds, temp)]

    ind = preds.index(max(preds))
    # print(preds)
    # print(max(preds))
    return d[ind]

# if __name__ == "__main__":

#     img = cv2.imread("plank_test.jpeg")

#     preds = run(img)

#     print(preds)


