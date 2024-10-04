import base64
import os
from joblib import load
from streamlit_option_menu import option_menu
from components.page_team_contact import contact_action, team_action
from components.page_mof_information import mof_inf_action
from components.get_ligand_feat import safe_generate_features,safe_generate_solvent_features
import streamlit as st
# from components.predict import PredictionModel
from models import NeuralNetwork_n_ratio
from models import NeuralNetwork_Vsyn_m
import pickle
import streamlit as st
import torch
import torch.nn as nn
import torch.nn.functional as F
import joblib
import pandas as pd
import numpy as np
import torch
import pandas as pd
import pymatgen.core as mg
import numpy as np
import joblib
import xgboost as xgb
from saved_models.models_list import (features_metal,MetalClassifier,TransformerClassifier,features_ligand,metal_columns,
                                      ligand_columns,features_solvent,solvent_columns,features_salt_mass,
                                      features_acid_mass,features_Vsyn,features_Tsyn,TransformerTsynClassifier,TransformerTdryClassifier,features_Tdry)


metal_molar_masses = {
        'Cu': 242, 
        'Zn': 297,
        'Al': 375,
        'Fe': 404,
        'Zr': 233,
        'Mg': 256,
        'La': 433,
        'Ce': 434,
        'Y': 383}

ligand_molar_masses = {
    'BTC': 207,
    'BDC': 164,
    'NH2-BDC': 179,
    'BTB': 435
}
            

def load_scaler(path):
    scaler = joblib.load(path)
    return scaler

def load_label_encoder(path):
    label_encoder = joblib.load(path)
    return label_encoder

# Load label encoders
label_encoder_major_metal = load_label_encoder('saved_scalers/label_encoder_major_metal.pkl')
label_encoder_minor_metal = load_label_encoder('saved_scalers/label_encoder_minor_metal.pkl')
label_encoder_ligand = load_label_encoder('saved_scalers/label_encoder_ligand.pkl')
label_encoder_solvent = load_label_encoder('saved_scalers/label_encoder_solvent.pkl')
label_encoder_Tsyn = load_label_encoder('saved_scalers/label_encoder_Tsyn.pkl')
label_encoder_Tdry = load_label_encoder('saved_scalers/label_encoder_Tdry.pkl')


scaler_binary_metals = load_scaler('saved_scalers/scaler_binary_metals.pkl')
scaler_major_metal = load_scaler('saved_scalers/scaler_major_metal.pkl')
scaler_minor_metal = load_scaler('saved_scalers/scaler_minor_metal.pkl')
scaler_ligand = load_scaler('saved_scalers/scaler_ligand.pkl')
scaler_solvent = load_scaler('saved_scalers/scaler_solvent.pkl')
scaler_salt_mass = load_scaler('saved_scalers/scaler_salt_mass.pkl')
scaler_acid_mass = load_scaler('saved_scalers/scaler_acid_mass.pkl')
scaler_Vsyn = load_scaler('saved_scalers/scaler_Vsyn.pkl')
scaler_Tsyn = load_scaler('saved_scalers/scaler_Tsyn.pkl')
scaler_Tdry = load_scaler('saved_scalers/scaler_Tdry.pkl')


def load_model(model_class,model_name, input_dim,num_classes=None):
    if num_classes!=None:
        model = model_class(input_dim=input_dim,num_classes=num_classes)
        model.load_state_dict(torch.load(f'saved_models/{model_name}.pth', map_location=torch.device('cpu'),weights_only=True))
        model.eval()
    else:
        model = model_class(input_dim=input_dim)
        model.load_state_dict(torch.load(f'saved_models/{model_name}.pth', map_location=torch.device('cpu'),weights_only=True))
        model.eval()
    return model

def load_xgb_model(path):
    model = xgb.Booster()
    model.load_model(path)
    return model


model_metal_binary_classifier = load_model(MetalClassifier,'dnn_metal_binary_classifier',len(features_metal))
model_major_metal = load_model(TransformerClassifier,'best_major_classifier_metal', len(features_metal),len(label_encoder_major_metal.classes_))
model_minor_metal = load_model(TransformerClassifier,'best_minor_classifier_metal',len(features_metal),len(label_encoder_minor_metal.classes_))
model_ligand = load_xgb_model('saved_models/xgb_ligand_classifier.json')
model_solvent = load_xgb_model('saved_models/xgb_solvent_classifier.json')
model_salt_mass= load_xgb_model('saved_models/xgb_mass_salt_classifier.json')
model_acid_mass= load_xgb_model('saved_models/xgb_acid_mass_regressor.json')
model_Vsyn= load_xgb_model('saved_models/model_xgb_V_syn_regressor.json')
model_Tsyn = load_model(TransformerTsynClassifier,'model_Tsyn',len(features_Tsyn),len(label_encoder_Tsyn.classes_))
model_Tdry = load_model(TransformerTdryClassifier,'model_Tdry',len(features_Tdry),len(label_encoder_Tdry.classes_))


st.set_page_config(
    layout="wide",
    page_title="adsorption AI platform",
    initial_sidebar_state="collapsed"
)

with open("static/style.css") as css_file:
    st.markdown('<style>{}</style>'.format(css_file.read()), unsafe_allow_html=True)


@st.cache_data
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


img = get_img_as_base64("images/background.jpg")

page_back = f"""
<style>

[data-testid="stAppViewContainer"]{{
background-image: url("data:image/png;base64,{img}");
# background-image: url("../images/background.jpg");
background-size: cover;
}}
</style>
"""

st.markdown(page_back, unsafe_allow_html=True)


def predict_action():
    st.title("Предсказание методики синтеза MOFs")

    page_style = f"""
    <style>
    .css-7mza0f {{
        border:3px solid white;
        padding:10px;
        background-color: white;
    }}
    </style>
    """

    st.markdown(page_style, unsafe_allow_html=True)
    
    # Ввод пользователем ключевых параметров
    SBAT_m2_gr = st.number_input("SБЭТ, м2/г - удельная площадь поверхности (от 100 до бесконечности)", min_value=100.0)
    a0_mmoll_gr = st.number_input("а0, ммоль/г - предельная адсорбция (от 0 до бесконечности)", min_value=0.0)
    E_kDg_moll = st.number_input("E,  кДж/моль - энергия адсорбции азота (от 0 до бесконечности)", min_value=0.0)
    
    # Расчет зависимых параметров
    # a) Объем микропор
    W0_cm3_g = 0.034692 * a0_mmoll_gr
    
    # б) Энергия адсорбции по бензолу (проверка на ноль)
    if E_kDg_moll > 0:
        E0_KDG_moll = E_kDg_moll / 0.33
    else:
        st.warning("Энергия адсорбции азота должна быть больше нуля для расчета энергии адсорбции по бензолу.")
        E0_KDG_moll = 1e-6  # или другое небольшое значение, чтобы избежать деления на ноль
    
    # в) Полуширина пор
    x0_nm = 12 / E0_KDG_moll
    
    # г) Общий объем пор (приблизительный)
    approx_Ws_cm3_gr = a0_mmoll_gr * 0.034692
    
    # Пользователь задает общий объем пор
    Ws_cm3_gr = st.number_input(
        f"Ws, см³/г - общий объем пор (приблизительное значение: {approx_Ws_cm3_gr:.4f} см³/г)", 
        min_value=0.0
    )
    
    # д) Объем мезопор
    Wme_cm3_gr = Ws_cm3_gr - W0_cm3_g
    
    # Пользователь задает площадь мезопор
    Sme_m2_gr = st.number_input("Sme, м2/г - площадь поверхности мезопор")

    # Вывод расчетных значений
    st.write(f"Объем микропор (W0): {W0_cm3_g:.4f} см³/г")
    st.write(f"Энергия адсорбции по бензолу (E0): {E0_KDG_moll:.4f} кДж/моль")
    st.write(f"Полуширина пор (x0): {x0_nm:.4f} нм")
    st.write(f"Объем мезопор (Wme): {Wme_cm3_gr:.4f} см³/г")
    
    # Создание DataFrame для расчетов и ввода
    data = {
        'SБЭТ, м2/г': [SBAT_m2_gr],
        'а0, ммоль/г': [a0_mmoll_gr],
        'E,  кДж/моль': [E_kDg_moll],
        'W0, см3/г': [W0_cm3_g],
        'Ws, см3/г': [Ws_cm3_gr],
        'E0, кДж/моль': [E0_KDG_moll],
        'х0, нм': [x0_nm],
        'Wme, см3/г': [Wme_cm3_gr],
        'Sme, м2/г': [Sme_m2_gr]
    }
    
    df = pd.DataFrame(data)
    
    # Расчет дополнительных параметров
    R = 8.314  # J/(mol·K)
    T = 298.15  # Kelvin (25°C)

    df['Adsorption_Potential'] = df['E,  кДж/моль'] * df['Ws, см3/г']
    df['Capacity_Density'] = df['а0, ммоль/г'] / df['SБЭТ, м2/г']
    df['K_equilibrium'] = np.exp(df['E,  кДж/моль'] / (R / 1000 * T))
    df['Delta_G'] = -R / 1000 * T * np.log(df['K_equilibrium'])
    df['SurfaceArea_MicroVol_Ratio'] = df['SБЭТ, м2/г'] / df['W0, см3/г']
    df['Adsorption_Energy_Ratio'] = df['E,  кДж/моль'] / df['E0, кДж/моль']
    df['S_BET_E'] = df['SБЭТ, м2/г'] * df['E,  кДж/моль']
    df['x0_W0'] = df['х0, нм'] * df['W0, см3/г']
    df["B_micropore"] = np.power(((2.3 * R) / df['E,  кДж/моль']), 2)
    
    # Отображение всех рассчитанных и введенных данных
    st.write("Рассчитанные и введенные параметры:")
    st.dataframe(df)

    # Добавляем кнопку для отправки на анализ
    if st.button("Отправить на анализ и получить методику синтеза"):
        
        with st.spinner('Пожалуйста, подождите...'):
            
            # ======================================
            # 1. Binary Metal Classification
            # ======================================
            
            input_scaled_binary = scaler_binary_metals.transform(df[features_metal].values)
            input_tensor_binary = torch.tensor(input_scaled_binary, dtype=torch.float32)
            
            with torch.no_grad():
                logits_binary = model_metal_binary_classifier(input_tensor_binary)
                prob_binary = torch.sigmoid(logits_binary)
                pred_binary = (prob_binary >= 0.5).int()
            
            # Map binary prediction to class
            class_mapping_binary = {0: 'La-Zn-Zr', 1: 'Cu-Al-Fe'}
            predicted_class_binary = class_mapping_binary.get(pred_binary.item(), "Unknown")
            
            st.success(f"**Binary Predicted Class:** {predicted_class_binary}")
            st.write(f"**Probability of 'Cu-Al-Fe':** {prob_binary.item():.4f}")
            st.write(f"**Probability of 'La-Zn-Zr':** {1 - prob_binary.item():.4f}")
            
            # ======================================
            # 2. Inner Metal Classification
            # ======================================
            predicted_metal = None
            
            if predicted_class_binary == 'Cu-Al-Fe':
                # Use major classes classifier
                input_scaled_major = scaler_major_metal.transform(df[features_metal].values)
                input_tensor_major = torch.tensor(input_scaled_major, dtype=torch.float32)
                
                with torch.no_grad():
                    logits_major = model_major_metal(input_tensor_major)
                    probs_major = F.softmax(logits_major, dim=1)
                    preds_major = torch.argmax(probs_major, dim=1)
                
                # Decode the prediction
                predicted_metal = label_encoder_major_metal.inverse_transform(preds_major.cpu().numpy())[0]
                
                st.write(f"**Inner Predicted Class (Cu-Al-Fe):** {predicted_metal}")
                st.write(f"**Probability:** {probs_major[0][preds_major].item():.4f}")
            
            elif predicted_class_binary == 'La-Zn-Zr':
                # Use minor classes classifier
                input_scaled_minor = scaler_minor_metal.transform(df[features_metal].values)
                input_tensor_minor = torch.tensor(input_scaled_minor, dtype=torch.float32)
                
                with torch.no_grad():
                    logits_minor = model_minor_metal(input_tensor_minor)
                    probs_minor = F.softmax(logits_minor, dim=1)
                    preds_minor = torch.argmax(probs_minor, dim=1)
                
                # Decode the prediction
                predicted_metal = label_encoder_minor_metal.inverse_transform(preds_minor.cpu().numpy())[0]
                
                st.write(f"**Inner Predicted Class (La-Zn-Zr):** {predicted_metal}")
                st.write(f"**Probability:** {probs_minor[0][preds_minor].item():.4f}")
            
            else:
                st.write("**Unable to determine the inner class due to an unknown binary prediction.**")
        

            # ======================================
            # 6. Ligand Classification
            # ======================================
            
            categorical_columns = []
            categorical_columns.extend(metal_columns)
            
            # One-Hot Encoding for 'Металл'
            for metal in metal_columns:
                metal_label = metal.split('_')[1]  # Extract 'Al', 'Cu', etc.
                df[metal] = 1 if metal_label == predicted_metal else 0
            
            df['Total molecular weight (metal)'] = mg.Composition(predicted_metal).weight
            df['Average ionic radius (metal)'] = mg.Element(mg.Composition(predicted_metal).elements[0]).average_ionic_radius
            df['Average electronegativity (metal)'] = mg.Composition(predicted_metal).average_electroneg
            
            
            # Scale the input for ligand classifier
            
            df_ligand = df[features_ligand].copy()
            numeric_columns = np.setdiff1d(df_ligand.columns, categorical_columns)
            df_ligand[numeric_columns] = scaler_ligand.transform(df_ligand[numeric_columns])

            # Create DMatrix for XGBoost
            dligand = xgb.DMatrix(df_ligand)
            
            # Predict probabilities for each class
            y_pred_proba_ligand = model_ligand.predict(dligand)
            
            # Since 'objective' was 'multi:softprob', the output is probability for each class
            y_pred_ligand = np.argmax(y_pred_proba_ligand, axis=1)
            y_pred_ligand_proba = y_pred_proba_ligand[np.arange(len(y_pred_ligand)), y_pred_ligand]
            
            # Decode the prediction
            predicted_class_ligand = label_encoder_ligand.inverse_transform(y_pred_ligand)[0]
            
            # Get probability for the predicted class
            prob_ligand = y_pred_ligand_proba[0]
            
            st.write(f"**Прогноз класса лиганда:** {predicted_class_ligand}")
            st.write(f"**Вероятность:** {prob_ligand:.4f}")
            
            
            # ======================================
            #  Solvent Classification
            # ======================================
            
            # One-Hot Encoding for 'Лиганд'
            for ligand in ligand_columns:
                ligand_label = ligand.split('_')[1] 
                df[ligand] = 1 if ligand_label == predicted_class_ligand else 0
                
                
            def add_ligand_descriptors_to_row(df_row):

                descriptors,new_columns = safe_generate_features(predicted_class_ligand)
                
                for column in new_columns:
                    df_row[column] = descriptors.get(column)
                
                return df_row

            # Apply the function to add descriptors
            df = df.apply(add_ligand_descriptors_to_row, axis=1)
            
            # Добавляем дескрипторы от солей и кислоты
            df["Молярка_соли"] = metal_molar_masses[predicted_metal]
            df["Молярка_кислоты"] = ligand_molar_masses[predicted_class_ligand]
            
            categorical_columns.extend(ligand_columns)
            
            # Scale the input for ligand classifier
            df_solvent = df[features_solvent].copy()
            numeric_columns = np.setdiff1d(df_solvent.columns, categorical_columns)
            df_solvent[numeric_columns] = scaler_solvent.transform(df_solvent[numeric_columns])

            # Create DMatrix for XGBoost
            dsolvent = xgb.DMatrix(df_solvent)
            
            # Predict probabilities for each class
            y_pred_proba_solvent = model_solvent.predict(dsolvent)
            
            # Since 'objective' was 'multi:softprob', the output is probability for each class
            y_pred_solvent = np.argmax(y_pred_proba_solvent, axis=1)
            y_pred_solvent_proba = y_pred_proba_solvent[np.arange(len(y_pred_solvent)), y_pred_solvent]
            
            # Decode the prediction
            predicted_class_solvent = label_encoder_solvent.inverse_transform(y_pred_solvent)[0]
            
            # Get probability for the predicted class
            prob_solvent = y_pred_solvent_proba[0]
            
            st.write(f"**Прогноз класса растворителя:** {predicted_class_solvent}")
            st.write(f"**Вероятность:** {prob_solvent:.4f}")
            
            # ======================================
            #  Salt mass prediction
            # ======================================
            
            # One-Hot Encoding for 'Растворитель'
            for solvent in solvent_columns:
                solvent_label = solvent.split('_')[1] 
                df[solvent] = 1 if solvent_label == predicted_class_solvent else 0
                
                
            def add_solvent_descriptors_to_row(df_row):

                descriptors,new_columns = safe_generate_solvent_features(predicted_class_solvent)
                
                for column in new_columns:
                    df_row[column] = descriptors.get(column)
                
                return df_row

            # Apply the function to add descriptors
            df = df.apply(add_solvent_descriptors_to_row, axis=1)
            
            categorical_columns.extend(solvent_columns)
            
            df_salt_mass = df[features_salt_mass].copy()
            numeric_columns = np.setdiff1d(df_salt_mass.columns, categorical_columns)
            df_salt_mass[numeric_columns] = scaler_salt_mass.transform(df_salt_mass[numeric_columns])

            # Create DMatrix for XGBoost
            dsalt_mass = xgb.DMatrix(df_salt_mass)
            
            # Predict probabilities for each class
            y_salt_mass_predicted = round(float(model_salt_mass.predict(dsalt_mass)[0]),3)
            
            st.write(f"**Прогноз значения массы соли:** {y_salt_mass_predicted}")
            
            df["m (соли), г"] = y_salt_mass_predicted
            
            df["n_соли"] = df["m (соли), г"]/df["Молярка_соли"]
            
            
            # ======================================
            #  Acid mass prediction
            # ======================================
            
            df_acid_mass = df[features_acid_mass].copy()
            numeric_columns = np.setdiff1d(df_acid_mass.columns, categorical_columns)
            df_acid_mass[numeric_columns] = scaler_acid_mass.transform(df_acid_mass[numeric_columns])

            # Create DMatrix for XGBoost
            dacid_mass = xgb.DMatrix(df_acid_mass)
            
            # Predict probabilities for each class
            y_acid_mass_predicted = round(float(model_acid_mass.predict(dacid_mass)[0]),3)
            
            st.write(f"**Прогноз значения массы кислоты:** {y_acid_mass_predicted}")
            
            df["m(кис-ты), г"] = y_acid_mass_predicted
            
            df["n_кислоты"] = df["m(кис-ты), г"]/df["Молярка_кислоты"]
            
            # ======================================
            #  Acid Volume prediction
            # ======================================
            
            df_Vsyn = df[features_Vsyn].copy()
            numeric_columns = np.setdiff1d(df_Vsyn.columns, categorical_columns)
            df_Vsyn[numeric_columns] = scaler_Vsyn.transform(df_Vsyn[numeric_columns])

            # Create DMatrix for XGBoost
            ddf_Vsyn = xgb.DMatrix(df_Vsyn)
            
            # Predict probabilities for each class
            Vsyn_predicted = round(float(model_Vsyn.predict(ddf_Vsyn)[0]),3)
            
            st.write(f"**Прогноз значения объема растворителя:** {Vsyn_predicted}")
            
            df["Vсин. (р-ля), мл"] = Vsyn_predicted
            
            # ======================================
            #  Temperature synthesis prediction
            # ======================================
    
            # Use major classes classifier
            
            df_Tsyn = df[features_Tsyn].copy()
            numeric_columns = np.setdiff1d(df_Tsyn.columns, categorical_columns)
            df_Tsyn[numeric_columns] = scaler_Tsyn.transform(df_Tsyn[numeric_columns].values)
            
            input_tensor_Tsyn = torch.tensor(df_Tsyn.values, dtype=torch.float32)
            
            with torch.no_grad():
                logits_major = model_Tsyn(input_tensor_Tsyn)
                probs_major = F.softmax(logits_major, dim=1)
                preds_major = torch.argmax(probs_major, dim=1)
            
            # Decode the prediction
            predicted_Tsyn = label_encoder_Tsyn.inverse_transform(preds_major.cpu().numpy())[0]
            
            st.write(f"**Predicted Temp.syn:** {predicted_Tsyn}")
            st.write(f"**Probability:** {probs_major[0][preds_major].item():.4f}")
            
            df["Т.син., °С"] = predicted_Tsyn
            
            # ======================================
            #  Temperature dry prediction
            # ======================================
            
            df_Tdry = df[features_Tdry].copy()
            numeric_columns = np.setdiff1d(df_Tdry.columns, categorical_columns)
            df_Tdry[numeric_columns] = scaler_Tdry.transform(df_Tdry[numeric_columns].values)
            
            input_tensor_Tdry = torch.tensor(df_Tdry.values, dtype=torch.float32)
            
            with torch.no_grad():
                logits_major = model_Tdry(input_tensor_Tdry)
                probs_major = F.softmax(logits_major, dim=1)
                preds_major = torch.argmax(probs_major, dim=1)
            
            # Decode the prediction
            predicted_Tdry = label_encoder_Tdry.inverse_transform(preds_major.cpu().numpy())[0]
            
            st.write(f"**Predicted Temp.dry:** {predicted_Tdry}")
            st.write(f"**Probability:** {probs_major[0][preds_major].item():.4f}")
            
            df["Т суш., °С"] = predicted_Tdry
            




def run():
    with st.sidebar:
        selected = option_menu(
            menu_title="𝐀𝐈 сервис пористых материалов",
            options=["О нас", "MOFs описание", "𝐀𝐈 синтез MOFs", "Контакты"],
            icons=["house", "book", "box fill", "list task", "person lines fill",
                   # "clipboard data fill",
                   "bar-chart-line-fill"],
            menu_icon="kanban fill",
            default_index=0,
            # orientation="horizontal",
            styles={
                "container": {"padding": "0 % 0 % 0 % 0 %"},
                "icon": {"color": "red", "font-size": "25px"},
                "nav-link": {"font-size": "20px", "text-align": "start", "margin": "0px"},
                "nav-link-selected": {"background-color": "#483D8B"},
            }

        )

    if selected == "О нас":
        team_image = "images/team.jpg"
        achievments_image = "images/achievments.jpg"
        team_action(team_image,achievments_image)
    if selected == "𝐀𝐈 синтез MOFs":
        predict_action()
    if selected == "MOFs описание":
        image1 = "images/1page.jpg"
        image2 = "images/2page.jpg"
        mof_inf_action(image1, image2)
    if selected == "Контакты":
        contact_action()


if __name__ == '__main__':
    run()
