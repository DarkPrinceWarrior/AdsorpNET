"""
Сервис для предсказания параметров синтеза MOF.
Содержит бизнес-логику для выполнения предсказаний.
"""

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import xgboost as xgb
import logging
from typing import Dict, Any, List, Tuple, Union, Optional
import pymatgen.core as mg

from src.services.model_service import ModelService
from src.domain.constants import METAL_MOLAR_MASSES, LIGAND_MOLAR_MASSES
from src.domain.features import (
    features_metal, features_ligand, features_solvent,
    features_salt_mass, features_acid_mass, features_Vsyn,
    features_Tsyn, features_Tdry, features_Treg,
    metal_columns, ligand_columns, solvent_columns
)
from src.utils.data.feature_generation import (
    safe_generate_features, safe_generate_solvent_features
)

logger = logging.getLogger(__name__)

class PredictorService:
    """
    Сервис для предсказания параметров синтеза MOF.
    """

    def __init__(self):
        """Инициализация сервиса предсказаний."""
        self.model_service = ModelService()
        
        # Используем то же устройство, что и в ModelService
        self.device = self.model_service.get_device()
        
        logger.info(f"Сервис предсказаний инициализирован (устройство: {self.device})")
        
    
    # Добавим метод в PredictorService для использования улучшенного кэширования

    def get_cached_prediction(self, input_params: Dict[str, float], prediction_type: str) -> Optional[Dict[str, Any]]:
        """
        Получает кэшированное предсказание, если оно существует.
        
        Args:
            input_params: Входные параметры
            prediction_type: Тип предсказания ('metal', 'ligand', 'solvent', и т.д.)
            
        Returns:
            Optional[Dict[str, Any]]: Результат предсказания или None
        """
        from src.utils.storage import create_cache_key, cached_prediction
        
        # Создаем ключ кэша
        cache_key = create_cache_key(input_params)
        
        # Получаем кэшированное предсказание
        model_name = f"{prediction_type.capitalize()}Classifier"
        result = cached_prediction(cache_key, model_name)
        
        if result is not None:
            logger.info(f"Получено кэшированное предсказание для {prediction_type}")
        
        return result

    def cache_prediction_result(self, input_params: Dict[str, float], prediction_type: str, result: Dict[str, Any]) -> None:
        """
        Кэширует результат предсказания.
        
        Args:
            input_params: Входные параметры
            prediction_type: Тип предсказания
            result: Результат предсказания
        """
        from src.utils.storage import create_cache_key, cached_prediction
        
        # Создаем ключ кэша
        cache_key = create_cache_key(input_params)
        
        # Сохраняем в кэш
        model_name = f"{prediction_type.capitalize()}Classifier"
        _ = cached_prediction(cache_key, model_name)  # Вызов для создания записи в LRU кэше
        cached_prediction.cache_info = result
        
        logger.info(f"Результат предсказания для {prediction_type} кэширован")

    def calculate_derived_features(
        self,
        SBAT_m2_gr: float,
        a0_mmoll_gr: float,
        E_kDg_moll: float,
        Ws_cm3_gr: float,
        Sme_m2_gr: float
    ) -> pd.DataFrame:
        """
        Рассчитывает производные признаки на основе базовых параметров.
        
        Args:
            SBAT_m2_gr: Удельная площадь поверхности (м²/г)
            a0_mmoll_gr: Предельная адсорбция (ммоль/г)
            E_kDg_moll: Энергия адсорбции азота (кДж/моль)
            Ws_cm3_gr: Общий объем пор (см³/г)
            Sme_m2_gr: Площадь поверхности мезопор (м²/г)
            
        Returns:
            pd.DataFrame: Датафрейм с рассчитанными параметрами
        """
        # Расчет объема микропор
        W0_cm3_g = 0.034692 * a0_mmoll_gr
        
        # Расчет энергии адсорбции по бензолу
        E0_KDG_moll = E_kDg_moll / 0.33 if E_kDg_moll > 0 else 1e-6
        
        # Расчет полуширины пор
        x0_nm = 12 / E0_KDG_moll
        
        # Расчет объема мезопор
        Wme_cm3_gr = Ws_cm3_gr - W0_cm3_g
        
        # Создаем DataFrame
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
        
        return df
    
    def predict_metal(self, features_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Предсказывает тип металла для MOF.
        
        Args:
            features_df: DataFrame с признаками
            
        Returns:
            Dict[str, Any]: Результаты предсказания (тип металла, вероятность)
        """
        # 1. Бинарная классификация металла
        binary_scaler = self.model_service.get_scaler('binary_metals')
        scaled_features = binary_scaler.transform(features_df[features_metal].values)
        
        # Используем устройство из экземпляра
        input_tensor = torch.tensor(scaled_features, dtype=torch.float32).to(self.device)
        
        binary_model = self.model_service.get_model('metal_binary')
        
        with torch.no_grad():
            logits = binary_model(input_tensor)
            prob = torch.sigmoid(logits)
            pred = (prob >= 0.5).int()
        
        class_mapping = {0: 'La-Zn-Zr', 1: 'Cu-Al-Fe'}
        predicted_class = class_mapping.get(pred.item(), "Unknown")
        
        # 2. Классификация конкретного металла
        if predicted_class == 'Cu-Al-Fe':
            # Используем классификатор основных металлов
            major_scaler = self.model_service.get_scaler('major_metal')
            scaled_features = major_scaler.transform(features_df[features_metal].values)
            input_tensor = torch.tensor(scaled_features, dtype=torch.float32).to(self.device)
            
            major_model = self.model_service.get_model('major_metal')
            encoder = self.model_service.get_encoder('major_metal')
            
            with torch.no_grad():
                logits = major_model(input_tensor)
                probs = F.softmax(logits, dim=1)
                preds = torch.argmax(probs, dim=1)
            
            predicted_metal = encoder.inverse_transform(preds.cpu().numpy())[0]
            metal_probability = probs[0][preds].item()
            
        elif predicted_class == 'La-Zn-Zr':
            # Используем классификатор второстепенных металлов
            minor_scaler = self.model_service.get_scaler('minor_metal')
            scaled_features = minor_scaler.transform(features_df[features_metal].values)
            input_tensor = torch.tensor(scaled_features, dtype=torch.float32).to(self.device)
            
            minor_model = self.model_service.get_model('minor_metal')
            encoder = self.model_service.get_encoder('minor_metal')
            
            with torch.no_grad():
                logits = minor_model(input_tensor)
                probs = F.softmax(logits, dim=1)
                preds = torch.argmax(probs, dim=1)
            
            predicted_metal = encoder.inverse_transform(preds.cpu().numpy())[0]
            metal_probability = probs[0][preds].item()
            
        else:
            return {
                'metal_type': None,
                'confidence': 0.0,
                'error': f"Unknown metal class: {predicted_class}"
            }
        
        return {
            'metal_type': predicted_metal,
            'confidence': metal_probability
        }
    
    def predict_ligand(self, features_df: pd.DataFrame, metal_type: str) -> Dict[str, Any]:
        """
        Предсказывает тип лиганда для MOF.
        
        Args:
            features_df: DataFrame с признаками
            metal_type: Тип металла
            
        Returns:
            Dict[str, Any]: Результаты предсказания (тип лиганда, вероятность)
        """
        # Обогащаем признаки информацией о металле
        df_ligand = features_df.copy()
        
        # One-Hot Encoding для металла
        for metal in metal_columns:
            metal_label = metal.split('_')[1]  # Extract 'Al', 'Cu', etc.
            df_ligand[metal] = 1 if metal_label == metal_type else 0
        
        # Добавляем дескрипторы металла
        df_ligand['Total molecular weight (metal)'] = mg.Composition(metal_type).weight
        df_ligand['Average ionic radius (metal)'] = mg.Element(mg.Composition(metal_type).elements[0]).average_ionic_radius
        df_ligand['Average electronegativity (metal)'] = mg.Composition(metal_type).average_electroneg
        
        # Масштабируем признаки
        ligand_scaler = self.model_service.get_scaler('ligand')
        categorical_columns = metal_columns
        numeric_columns = np.setdiff1d(features_ligand, categorical_columns)
        
        df_ligand_numeric = df_ligand[numeric_columns].copy()
        df_ligand_numeric = pd.DataFrame(
            ligand_scaler.transform(df_ligand_numeric),
            columns=numeric_columns
        )
        
        # Объединяем числовые и категориальные признаки
        for col in categorical_columns:
            if col in df_ligand.columns:
                df_ligand_numeric[col] = df_ligand[col]
        
        # Создаем DMatrix для XGBoost
        dligand = xgb.DMatrix(df_ligand_numeric[features_ligand])
        
        # Получаем модель и делаем предсказание
        ligand_model = self.model_service.get_model('ligand')
        encoder = self.model_service.get_encoder('ligand')
        
        y_pred_proba = ligand_model.predict(dligand)
        y_pred = np.argmax(y_pred_proba, axis=1)
        y_pred_proba_max = y_pred_proba[np.arange(len(y_pred)), y_pred]
        
        # Декодируем предсказание
        predicted_ligand = encoder.inverse_transform(y_pred)[0]
        ligand_probability = y_pred_proba_max[0]
        
        # Формируем словарь с вероятностями для всех классов
        probabilities = {
            ligand: float(prob)
            for ligand, prob in zip(encoder.classes_, y_pred_proba[0])
        }
        
        return {
            'ligand_type': predicted_ligand,
            'confidence': ligand_probability,
            'all_probabilities': probabilities
        }
    
    def predict_solvent(
        self, 
        features_df: pd.DataFrame, 
        metal_type: str, 
        ligand_type: str
    ) -> Dict[str, Any]:
        """
        Предсказывает тип растворителя для MOF.
        
        Args:
            features_df: DataFrame с признаками
            metal_type: Тип металла
            ligand_type: Тип лиганда
            
        Returns:
            Dict[str, Any]: Результаты предсказания (тип растворителя, вероятность)
        """
        # Обогащаем признаки информацией о металле и лиганде
        df_solvent = features_df.copy()
        
        # One-Hot Encoding для металла
        for metal in metal_columns:
            metal_label = metal.split('_')[1]
            df_solvent[metal] = 1 if metal_label == metal_type else 0
        
        # Добавляем дескрипторы металла
        df_solvent['Total molecular weight (metal)'] = mg.Composition(metal_type).weight
        df_solvent['Average ionic radius (metal)'] = mg.Element(mg.Composition(metal_type).elements[0]).average_ionic_radius
        df_solvent['Average electronegativity (metal)'] = mg.Composition(metal_type).average_electroneg
        
        # Добавляем информацию о молярных массах
        df_solvent["Молярка_соли"] = METAL_MOLAR_MASSES[metal_type]
        df_solvent["Молярка_кислоты"] = LIGAND_MOLAR_MASSES[ligand_type]
        
        # One-Hot Encoding для лиганда
        for ligand in ligand_columns:
            ligand_label = ligand.split('_')[1]
            df_solvent[ligand] = 1 if ligand_label == ligand_type else 0
            
        # Добавляем дескрипторы лиганда
        ligand_descriptors, _ = safe_generate_features(ligand_type)
        for column, value in ligand_descriptors.items():
            df_solvent[column] = value
        
        # Масштабируем признаки
        solvent_scaler = self.model_service.get_scaler('solvent')
        categorical_columns = metal_columns + ligand_columns
        numeric_columns = np.setdiff1d(features_solvent, categorical_columns)
        
        df_solvent_numeric = df_solvent[numeric_columns].copy()
        df_solvent_numeric = pd.DataFrame(
            solvent_scaler.transform(df_solvent_numeric),
            columns=numeric_columns
        )
        
        # Объединяем числовые и категориальные признаки
        for col in categorical_columns:
            if col in df_solvent.columns:
                df_solvent_numeric[col] = df_solvent[col]
        
        # Создаем DMatrix для XGBoost
        dsolvent = xgb.DMatrix(df_solvent_numeric[features_solvent])
        
        # Получаем модель и делаем предсказание
        solvent_model = self.model_service.get_model('solvent')
        encoder = self.model_service.get_encoder('solvent')
        
        y_pred_proba = solvent_model.predict(dsolvent)
        y_pred = np.argmax(y_pred_proba, axis=1)
        y_pred_proba_max = y_pred_proba[np.arange(len(y_pred)), y_pred]
        
        # Декодируем предсказание
        predicted_solvent = encoder.inverse_transform(y_pred)[0]
        solvent_probability = y_pred_proba_max[0]
        
        # Формируем словарь с вероятностями для всех классов
        probabilities = {
            solvent: float(prob)
            for solvent, prob in zip(encoder.classes_, y_pred_proba[0])
        }
        
        # Сортируем растворители по убыванию вероятности
        sorted_solvents = sorted(
            probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'solvent_type': predicted_solvent,
            'confidence': solvent_probability,
            'all_probabilities': probabilities,
            'top_3_solvents': [
                {'type': solv, 'probability': prob}
                for solv, prob in sorted_solvents[:3]
            ]
        }
    
    def predict_salt_mass(
        self, 
        features_df: pd.DataFrame, 
        metal_type: str, 
        ligand_type: str, 
        solvent_type: str
    ) -> float:
        """
        Предсказывает массу соли для синтеза MOF.
        
        Args:
            features_df: DataFrame с признаками
            metal_type: Тип металла
            ligand_type: Тип лиганда
            solvent_type: Тип растворителя
            
        Returns:
            float: Предсказанная масса соли
        """
        # Обогащаем признаки информацией о металле, лиганде и растворителе
        df_salt = features_df.copy()
        
        # One-Hot Encoding для металла
        for metal in metal_columns:
            metal_label = metal.split('_')[1]
            df_salt[metal] = 1 if metal_label == metal_type else 0
        
        # Добавляем дескрипторы металла
        df_salt['Total molecular weight (metal)'] = mg.Composition(metal_type).weight
        df_salt['Average ionic radius (metal)'] = mg.Element(mg.Composition(metal_type).elements[0]).average_ionic_radius
        df_salt['Average electronegativity (metal)'] = mg.Composition(metal_type).average_electroneg
        
        # Добавляем информацию о молярных массах
        df_salt["Молярка_соли"] = METAL_MOLAR_MASSES[metal_type]
        df_salt["Молярка_кислоты"] = LIGAND_MOLAR_MASSES[ligand_type]
        
        # One-Hot Encoding для лиганда
        for ligand in ligand_columns:
            ligand_label = ligand.split('_')[1]
            df_salt[ligand] = 1 if ligand_label == ligand_type else 0
            
        # Добавляем дескрипторы лиганда
        ligand_descriptors, _ = safe_generate_features(ligand_type)
        for column, value in ligand_descriptors.items():
            df_salt[column] = value
        
        # One-Hot Encoding для растворителя
        for solvent in solvent_columns:
            solvent_label = solvent.split('_')[1]
            df_salt[solvent] = 1 if solvent_label == solvent_type else 0
            
        # Добавляем дескрипторы растворителя
        solvent_descriptors, _ = safe_generate_solvent_features(solvent_type)
        for column, value in solvent_descriptors.items():
            df_salt[column] = value
        
        # Масштабируем признаки
        salt_scaler = self.model_service.get_scaler('salt_mass')
        categorical_columns = metal_columns + ligand_columns + solvent_columns
        numeric_columns = np.setdiff1d(features_salt_mass, categorical_columns)
        
        df_salt_numeric = df_salt[numeric_columns].copy()
        df_salt_numeric = pd.DataFrame(
            salt_scaler.transform(df_salt_numeric),
            columns=numeric_columns
        )
        
        # Объединяем числовые и категориальные признаки
        for col in categorical_columns:
            if col in df_salt.columns:
                df_salt_numeric[col] = df_salt[col]
        
        # Создаем DMatrix для XGBoost
        dsalt = xgb.DMatrix(df_salt_numeric[features_salt_mass])
        
        # Получаем модель и делаем предсказание
        salt_model = self.model_service.get_model('salt_mass')
        
        salt_mass = float(salt_model.predict(dsalt)[0])
        return round(salt_mass, 3)
    
    def predict_acid_mass(
        self, 
        features_df: pd.DataFrame, 
        metal_type: str, 
        ligand_type: str, 
        solvent_type: str, 
        salt_mass: float
    ) -> float:
        """
        Предсказывает массу кислоты для синтеза MOF.
        
        Args:
            features_df: DataFrame с признаками
            metal_type: Тип металла
            ligand_type: Тип лиганда
            solvent_type: Тип растворителя
            salt_mass: Масса соли
            
        Returns:
            float: Предсказанная масса кислоты
        """
        # Аналогично salt_mass, но добавляем информацию о массе соли
        df_acid = features_df.copy()
        
        # Заполняем признаки как в предыдущих методах
        # (металл, лиганд, растворитель)
        
        # One-Hot Encoding для металла
        for metal in metal_columns:
            metal_label = metal.split('_')[1]
            df_acid[metal] = 1 if metal_label == metal_type else 0
        
        # Добавляем дескрипторы металла
        df_acid['Total molecular weight (metal)'] = mg.Composition(metal_type).weight
        df_acid['Average ionic radius (metal)'] = mg.Element(mg.Composition(metal_type).elements[0]).average_ionic_radius
        df_acid['Average electronegativity (metal)'] = mg.Composition(metal_type).average_electroneg
        
        # Добавляем информацию о молярных массах
        df_acid["Молярка_соли"] = METAL_MOLAR_MASSES[metal_type]
        df_acid["Молярка_кислоты"] = LIGAND_MOLAR_MASSES[ligand_type]
        
        # One-Hot Encoding для лиганда
        for ligand in ligand_columns:
            ligand_label = ligand.split('_')[1]
            df_acid[ligand] = 1 if ligand_label == ligand_type else 0
            
        # Добавляем дескрипторы лиганда
        ligand_descriptors, _ = safe_generate_features(ligand_type)
        for column, value in ligand_descriptors.items():
            df_acid[column] = value
        
        # One-Hot Encoding для растворителя
        for solvent in solvent_columns:
            solvent_label = solvent.split('_')[1]
            df_acid[solvent] = 1 if solvent_label == solvent_type else 0
            
        # Добавляем дескрипторы растворителя
        solvent_descriptors, _ = safe_generate_solvent_features(solvent_type)
        for column, value in solvent_descriptors.items():
            df_acid[column] = value
            
        # Добавляем информацию о массе соли
        df_acid["m (соли), г"] = salt_mass
        df_acid["n_соли"] = salt_mass / METAL_MOLAR_MASSES[metal_type]
        
        # Масштабируем признаки
        acid_scaler = self.model_service.get_scaler('acid_mass')
        categorical_columns = metal_columns + ligand_columns + solvent_columns
        numeric_columns = np.setdiff1d(features_acid_mass, categorical_columns)
        
        df_acid_numeric = df_acid[numeric_columns].copy()
        df_acid_numeric = pd.DataFrame(
            acid_scaler.transform(df_acid_numeric),
            columns=numeric_columns
        )
        
        # Объединяем числовые и категориальные признаки
        for col in categorical_columns:
            if col in df_acid.columns:
                df_acid_numeric[col] = df_acid[col]
        
        # Создаем DMatrix для XGBoost
        dacid = xgb.DMatrix(df_acid_numeric[features_acid_mass])
        
        # Получаем модель и делаем предсказание
        acid_model = self.model_service.get_model('acid_mass')
        
        acid_mass = float(acid_model.predict(dacid)[0])
        return round(acid_mass, 3)

    def predict_synthesis_volume(
        self,
        features_df: pd.DataFrame,
        metal_type: str,
        ligand_type: str,
        solvent_type: str,
        salt_mass: float,
        acid_mass: float
    ) -> float:
        """
        Предсказывает объем синтеза MOF.
        
        Args:
            features_df: DataFrame с признаками
            metal_type: Тип металла
            ligand_type: Тип лиганда
            solvent_type: Тип растворителя
            salt_mass: Масса соли
            acid_mass: Масса кислоты
            
        Returns:
            float: Предсказанный объем синтеза
        """
        # Аналогично предыдущим, но добавляем информацию о массе соли и кислоты
        df_vsyn = features_df.copy()
        
        # Заполняем признаки как в предыдущих методах
        # (металл, лиганд, растворитель, масса соли)
        
        # One-Hot Encoding для металла
        for metal in metal_columns:
            metal_label = metal.split('_')[1]
            df_vsyn[metal] = 1 if metal_label == metal_type else 0
        
        # Добавляем дескрипторы металла
        df_vsyn['Total molecular weight (metal)'] = mg.Composition(metal_type).weight
        df_vsyn['Average ionic radius (metal)'] = mg.Element(mg.Composition(metal_type).elements[0]).average_ionic_radius
        df_vsyn['Average electronegativity (metal)'] = mg.Composition(metal_type).average_electroneg
        
        # Добавляем информацию о молярных массах
        df_vsyn["Молярка_соли"] = METAL_MOLAR_MASSES[metal_type]
        df_vsyn["Молярка_кислоты"] = LIGAND_MOLAR_MASSES[ligand_type]
        
        # One-Hot Encoding для лиганда
        for ligand in ligand_columns:
            ligand_label = ligand.split('_')[1]
            df_vsyn[ligand] = 1 if ligand_label == ligand_type else 0
            
        # Добавляем дескрипторы лиганда
        ligand_descriptors, _ = safe_generate_features(ligand_type)
        for column, value in ligand_descriptors.items():
            df_vsyn[column] = value
        
        # One-Hot Encoding для растворителя
        for solvent in solvent_columns:
            solvent_label = solvent.split('_')[1]
            df_vsyn[solvent] = 1 if solvent_label == solvent_type else 0
            
        # Добавляем дескрипторы растворителя
        solvent_descriptors, _ = safe_generate_solvent_features(solvent_type)
        for column, value in solvent_descriptors.items():
            df_vsyn[column] = value
            
        # Добавляем информацию о массе соли и кислоты
        df_vsyn["m (соли), г"] = salt_mass
        df_vsyn["n_соли"] = salt_mass / METAL_MOLAR_MASSES[metal_type]
        df_vsyn["m(кис-ты), г"] = acid_mass
        df_vsyn["n_кислоты"] = acid_mass / LIGAND_MOLAR_MASSES[ligand_type]
        
        # Масштабируем признаки
        vsyn_scaler = self.model_service.get_scaler('Vsyn')
        categorical_columns = metal_columns + ligand_columns + solvent_columns
        numeric_columns = np.setdiff1d(features_Vsyn, categorical_columns)
        
        df_vsyn_numeric = df_vsyn[numeric_columns].copy()
        df_vsyn_numeric = pd.DataFrame(
            vsyn_scaler.transform(df_vsyn_numeric),
            columns=numeric_columns
        )
        
        # Объединяем числовые и категориальные признаки
        for col in categorical_columns:
            if col in df_vsyn.columns:
                df_vsyn_numeric[col] = df_vsyn[col]
        
        # Создаем DMatrix для XGBoost
        dvsyn = xgb.DMatrix(df_vsyn_numeric[features_Vsyn])
        
        # Получаем модель и делаем предсказание
        vsyn_model = self.model_service.get_model('Vsyn')
        
        vsyn = float(vsyn_model.predict(dvsyn)[0])
        return round(vsyn, 3)
    
    def predict_temperature(
        self,
        features_df: pd.DataFrame,
        metal_type: str,
        ligand_type: str,
        solvent_type: str,
        salt_mass: float,
        acid_mass: float,
        vsyn: float = None,
        tsyn: float = None,
        tdry: float = None,
        temp_type: str = 'Tsyn'
    ) -> Dict[str, Any]:
        """
        Предсказывает температуру для синтеза, сушки или регенерации MOF.
        
        Args:
            features_df: DataFrame с признаками
            metal_type: Тип металла
            ligand_type: Тип лиганда
            solvent_type: Тип растворителя
            salt_mass: Масса соли
            acid_mass: Масса кислоты
            vsyn: Объем синтеза
            tsyn: Температура синтеза (для Tdry и Treg)
            tdry: Температура сушки (для Treg)
            temp_type: Тип температуры ('Tsyn', 'Tdry', 'Treg')
            
        Returns:
            Dict[str, Any]: Результаты предсказания (температура, вероятность)
        """
        # Подготавливаем DataFrame с признаками
        df_temp = features_df.copy()
        
        # Заполняем признаки как в предыдущих методах
        # (металл, лиганд, растворитель, масса соли, масса кислоты)
        
        # One-Hot Encoding для металла
        for metal in metal_columns:
            metal_label = metal.split('_')[1]
            df_temp[metal] = 1 if metal_label == metal_type else 0
        
        # Добавляем дескрипторы металла
        df_temp['Total molecular weight (metal)'] = mg.Composition(metal_type).weight
        df_temp['Average ionic radius (metal)'] = mg.Element(mg.Composition(metal_type).elements[0]).average_ionic_radius
        df_temp['Average electronegativity (metal)'] = mg.Composition(metal_type).average_electroneg
        
        # Добавляем информацию о молярных массах
        df_temp["Молярка_соли"] = METAL_MOLAR_MASSES[metal_type]
        df_temp["Молярка_кислоты"] = LIGAND_MOLAR_MASSES[ligand_type]
        
        # One-Hot Encoding для лиганда
        for ligand in ligand_columns:
            ligand_label = ligand.split('_')[1]
            df_temp[ligand] = 1 if ligand_label == ligand_type else 0
            
        # Добавляем дескрипторы лиганда
        ligand_descriptors, _ = safe_generate_features(ligand_type)
        for column, value in ligand_descriptors.items():
            df_temp[column] = value
        
        # One-Hot Encoding для растворителя
        for solvent in solvent_columns:
            solvent_label = solvent.split('_')[1]
            df_temp[solvent] = 1 if solvent_label == solvent_type else 0
            
        # Добавляем дескрипторы растворителя
        solvent_descriptors, _ = safe_generate_solvent_features(solvent_type)
        for column, value in solvent_descriptors.items():
            df_temp[column] = value
            
        # Добавляем информацию о массе соли и кислоты
        df_temp["m (соли), г"] = salt_mass
        df_temp["n_соли"] = salt_mass / METAL_MOLAR_MASSES[metal_type]
        df_temp["m(кис-ты), г"] = acid_mass
        df_temp["n_кислоты"] = acid_mass / LIGAND_MOLAR_MASSES[ligand_type]
        
        # Добавляем информацию об объеме синтеза, если указано
        if vsyn is not None:
            df_temp["Vсин. (р-ля), мл"] = vsyn
            
        # Добавляем информацию о температуре синтеза, если указано
        if tsyn is not None:
            df_temp["Т.син., °С"] = tsyn
            
        # Добавляем информацию о температуре сушки, если указано
        if tdry is not None:
            df_temp["Т суш., °С"] = tdry
            
        # Выбираем признаки и скейлер в зависимости от типа температуры
        if temp_type == 'Tsyn':
            features = features_Tsyn
            scaler_name = 'Tsyn'
            model_name = 'Tsyn'
        elif temp_type == 'Tdry':
            features = features_Tdry
            scaler_name = 'Tdry'
            model_name = 'Tdry'
        elif temp_type == 'Treg':
            features = features_Treg
            scaler_name = 'Treg'
            model_name = 'Treg'
        else:
            raise ValueError(f"Неизвестный тип температуры: {temp_type}")
            
        # Масштабируем признаки
        temp_scaler = self.model_service.get_scaler(scaler_name)
        categorical_columns = metal_columns + ligand_columns + solvent_columns
        
        # Проверяем, что все нужные признаки есть в df_temp
        for feature in features:
            if feature not in df_temp.columns and feature not in categorical_columns:
                logger.warning(f"Feature '{feature}' not found in DataFrame")
        
        numeric_columns = np.setdiff1d(features, categorical_columns)
        
        df_temp_numeric = df_temp[numeric_columns].copy()
        df_temp_numeric = pd.DataFrame(
            temp_scaler.transform(df_temp_numeric),
            columns=numeric_columns
        )
        
        # Объединяем числовые и категориальные признаки
        for col in categorical_columns:
            if col in df_temp.columns and col in features:
                df_temp_numeric[col] = df_temp[col]
        
        # Преобразуем в тензор для PyTorch
        input_tensor = torch.tensor(df_temp_numeric[features].values, dtype=torch.float32).to(self.device)
        
        # Получаем модель и энкодер
        temp_model = self.model_service.get_model(model_name)
        encoder = self.model_service.get_encoder(scaler_name)
        
        # Делаем предсказание
        with torch.no_grad():
            logits = temp_model(input_tensor)
            probs = F.softmax(logits, dim=1)
            preds = torch.argmax(probs, dim=1)
        
        # Декодируем предсказание
        predicted_temp = encoder.inverse_transform(preds.cpu().numpy())[0]
        temp_probability = probs[0][preds].item()
        
        # Формируем словарь с вероятностями для всех классов
        probabilities = {
            str(temp): float(prob)
            for temp, prob in zip(encoder.classes_, probs[0].cpu().numpy())
        }
        
        # Сортируем температуры по убыванию вероятности
        sorted_temps = sorted(
            probabilities.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            'temperature': predicted_temp,
            'confidence': temp_probability,
            'all_probabilities': probabilities,
            'top_3_temperatures': [
                {'value': temp, 'probability': prob}
                for temp, prob in sorted_temps[:3]
            ]
        }
    
    def run_full_prediction(
        self,
        SBAT_m2_gr: float,
        a0_mmoll_gr: float,
        E_kDg_moll: float,
        Ws_cm3_gr: float,
        Sme_m2_gr: float
    ) -> Dict[str, Any]:
        """
        Выполняет полное предсказание всех параметров синтеза MOF.
        
        Args:
            SBAT_m2_gr: Удельная площадь поверхности (м²/г)
            a0_mmoll_gr: Предельная адсорбция (ммоль/г)
            E_kDg_moll: Энергия адсорбции азота (кДж/моль)
            Ws_cm3_gr: Общий объем пор (см³/г)
            Sme_m2_gr: Площадь поверхности мезопор (м²/г)
            
        Returns:
            Dict[str, Any]: Результаты всех предсказаний
        """
        # Рассчитываем производные признаки
        features_df = self.calculate_derived_features(
            SBAT_m2_gr, a0_mmoll_gr, E_kDg_moll, Ws_cm3_gr, Sme_m2_gr
        )
        
        # Предсказываем тип металла
        metal_result = self.predict_metal(features_df)
        metal_type = metal_result['metal_type']
        
        # Предсказываем тип лиганда
        ligand_result = self.predict_ligand(features_df, metal_type)
        ligand_type = ligand_result['ligand_type']
        
        # Предсказываем тип растворителя
        solvent_result = self.predict_solvent(features_df, metal_type, ligand_type)
        solvent_type = solvent_result['solvent_type']
        
        # Предсказываем массу соли
        salt_mass = self.predict_salt_mass(features_df, metal_type, ligand_type, solvent_type)
        
        # Предсказываем массу кислоты
        acid_mass = self.predict_acid_mass(features_df, metal_type, ligand_type, solvent_type, salt_mass)
        
        # Предсказываем объем синтеза
        vsyn = self.predict_synthesis_volume(features_df, metal_type, ligand_type, solvent_type, salt_mass, acid_mass)
        
        # Предсказываем температуру синтеза
        tsyn_result = self.predict_temperature(
            features_df, metal_type, ligand_type, solvent_type, salt_mass, acid_mass, vsyn, 
            temp_type='Tsyn'
        )
        tsyn = tsyn_result['temperature']
        
        # Предсказываем температуру сушки
        tdry_result = self.predict_temperature(
            features_df, metal_type, ligand_type, solvent_type, salt_mass, acid_mass, vsyn, tsyn, 
            temp_type='Tdry'
        )
        tdry = tdry_result['temperature']
        
        # Предсказываем температуру регенерации
        treg_result = self.predict_temperature(
            features_df, metal_type, ligand_type, solvent_type, salt_mass, acid_mass, vsyn, tsyn, tdry, 
            temp_type='Treg'
        )
        
        # Формируем результат
        return {
            'metal': metal_result,
            'ligand': ligand_result,
            'solvent': solvent_result,
            'salt_mass': salt_mass,
            'acid_mass': acid_mass,
            'synthesis_volume': vsyn,
            'tsyn': tsyn_result,
            'tdry': tdry_result,
            'treg': treg_result,
            'derived_features': {
                'W0_cm3_g': features_df['W0, см3/г'][0],
                'E0_KDG_moll': features_df['E0, кДж/моль'][0],
                'x0_nm': features_df['х0, нм'][0],
                'Wme_cm3_gr': features_df['Wme, см3/г'][0]
            }
        }