import numpy as np
import os
import pandas as pd
import json
   
# d={
#     "GeneralContractualServices":"Service",
#     "Professional":"Service",
#     "Technical":"Service",
#     "Advertisement":"Service",
#     "Commissions":"Service",
#     "Transportation":"Service",
#     "CallCentreServices":"Service",
#     "Rent_Ib":"Rent",
#     "Rent_Ia":"Rent",
#     "Goods":"Goods",
#     "RoyaltyOther":"Royalty",
#     "Royalty":"Royalty",
#     "NonTaxable":"Nonreportable"
#     }

def input_fn(input_data, request_content_type):
    if request_content_type == "application/json":
        sentence = json.loads(input_data)
        return sentence
    
def predict_fn(input_data, model):
    listed = []
    for i in range(len(input_data)):
        listed.append({"Intent":input_data[i]["label"][0][9:],"Intent_confidence":input_data[i]["prob"][0]*100,"index":i})
#         listed.append({"Level : 1":{"Intent":d[i["label"][0][9:]],"Intent Confidence":i["prob"][0]*100},"Level : 2":{"Intent ":i["label"][0][9:],"Scores:":{"Intent 1":i["label"][0][9:],"Intent 1 Confidence":i["prob"][0]*100,"Intent 2":i["label"][1][9:],"Intent 2 Confidence":i["prob"][1]*100,"Intent 3":i["label"][2][9:],"Intent 3 Confidence":i["prob"][2]*100}}})
    return listed
    
# returning in the format suitable for the blazing text
def output_fn(prediction, response_content_type):
    return {"Inference":prediction}

def model_fn(model_dir):
#     preprocessor = joblib.load(os.path.join(model_dir, "model.joblib"))
    return 1