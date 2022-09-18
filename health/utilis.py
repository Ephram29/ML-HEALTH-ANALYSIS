import pandas as pd
import os
from django.contrib.auth.models import User
from pathlib import Path
import csv
import pickle
from .models import symptoms as Symptoms
import numpy as np
from statistics import mean
from django.shortcuts import render
BASE_DIR = Path(__file__).resolve().parent.parent
df_norm = pd.read_csv(str(BASE_DIR)+'\ml\dataset\dis_sym_dataset_norm.csv', sep=',')
#test_data = df_norm.drop('prognosis', axis=1)
with open(str(BASE_DIR)+"/ml/dataset/symptoms.pkl", "rb") as fp:
    symptoms = pickle.load(fp)
with open(str(BASE_DIR)+"\ml\dataset\list_diseaseNames.pkl", "rb") as fp:
    diseases = pickle.load(fp)
fields = []
description = {}
precautionDictionary = {}
#ml models
model = pickle.load(open(str(BASE_DIR)+'/ml/symptoms_model(92.31).pkl', 'rb'))
diabetes_mod=pickle.load(open(str(BASE_DIR)+'/ml/classifier.pkl','rb'))
sc=pickle.load(open(str(BASE_DIR)+'/ml/sc.pkl','rb'))
with open(str(BASE_DIR)+'/ml/disease_description.csv', encoding="utf8") as csvfile:
    csvreader = csv.reader(csvfile)
    fields = next(csvreader)

    for row in csvreader:
        disease, desc = row
        description[disease] = desc

with open(str(BASE_DIR)+'/ml/symptom_precaution.csv', encoding="utf8") as csv_file:

    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        _prec = {row[0]: [row[1], row[2], row[3], row[4]]}
        precautionDictionary.update(_prec)
#print(precautionDictionary)
def get_intent(text):
    intents = {"greeting": ["hi", "hello", "hey", "symptoms"], "ask_symptoms": symptoms, "ask_symptoms-no": ["no","No"], "end-chat": ["bye", "thanks", "thankyou", "fine", "okay","ok","thank you"]}
    words = text.lower().split(" ")
    #print(words)
    real_intent = ''
    for word in words:
        for intent in intents:
            #print(intent)
            if word in intents[intent]:
                real_intent = intent
                return real_intent
            elif intent == "ask_symptoms":
                for each_symp in intents[intent]:
                    splitted_symptoms=each_symp.split()
                    if word in splitted_symptoms:
                        real_intent = intent
                        return real_intent


def predict_disease(affected_symps,final_symp):
    prediction = model.predict_proba([affected_symps])
    k = 10
    #diseases = list(set(Y['label_dis']))
    #print("prediction=",prediction)
    diseases.sort()
    scores = [0.78213922,0.87945671,0.92473118,0.94793435,0.97792869]
    final_symp=set(final_symp)
    topk = prediction[0].argsort()[-k:][::-1]
    #print("topk=",topk)
    print(f"\nTop {k} diseases predicted based on symptoms")
    topk_dict = {}
    # Show top 10 highly probable disease to the user.
    for idx, t in enumerate(topk):
        match_sym = set()
        row = df_norm.loc[df_norm['label_dis'] == diseases[t]].values.tolist()
        row[0].pop(0)

        for idx, val in enumerate(row[0]):
            if val != 0:
                match_sym.add(symptoms[idx])
        prob = (len(match_sym.intersection(set(final_symp)))+1) / \
            (len(set(final_symp))+1)
        prob *= mean(scores)
        topk_dict[t] = prob
    j = 0
    topk_index_mapping = {}
    probab_diseases=[]
    topk_sorted = dict(
        sorted(topk_dict.items(), key=lambda kv: kv[1], reverse=True))
    for key in topk_sorted:
        prob = topk_sorted[key]*100
        print(str(j) + " Disease name:",
                diseases[key], "\tProbability:", str(round(prob, 2))+"%")
        probab_diseases.append(diseases[key])
        topk_index_mapping[j] = key
        j += 1
    return probab_diseases
#updated symptoms to db

'''def update_symptoms(request):
    for symptom in symptoms:
        Symptoms(symptom_name=str(symptom),symptom_desc="").save()'''





def predict_diabetes(request):
    float_features = [
        float(x) for key, x in request.POST.items() if key != "csrfmiddlewaretoken"]
    final_features = [np.array(float_features)]
    print(sc.transform(final_features))
    pred = diabetes_mod.predict( sc.transform(final_features) )
    return render(request, "diabeticform.html", {'prediction': pred, 'age': request.user.profile.age}), pred


    
