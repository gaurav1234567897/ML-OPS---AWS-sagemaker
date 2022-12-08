import json
import pathlib
import pickle
import tarfile
import joblib
import numpy as np
import pandas as pd
import subprocess
from sklearn.metrics import accuracy_score
subprocess.run("pip install wheel",shell=True)
subprocess.run("pip install fasttext",shell=True)
import fasttext
if __name__ == "__main__":
    model_path = "/opt/ml/processing/model/model.tar.gz"
    with tarfile.open(model_path) as tar:
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(tar, path=".")

    model = fasttext.load_model('model.bin')

    test_path = "/opt/ml/processing/test/test.csv"
    df = pd.read_csv(test_path)
    pred = []
    for i in df.Text:
        pred.append(str(model.predict(i)[0])[11:-3])
        
    accuracy = accuracy_score(df.label, pred)
    report_dict = {
        "classification_metrics": {
            "accuracy": {"value": accuracy},
        },
    }

    output_dir = "/opt/ml/processing/evaluation"
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    evaluation_path = f"{output_dir}/evaluation.json"
    with open(evaluation_path, "w") as f:
        f.write(json.dumps(report_dict))
