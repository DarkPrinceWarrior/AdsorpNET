import numpy as np
import xgboost as xgb
import logging
from typing import Dict, Any, List
from .base_model import BaseModel
from ..config import MODEL_CONFIG, SCALER_CONFIG
import joblib

logger = logging.getLogger(__name__)

class LigandClassifier(BaseModel):
    """Классификатор для определения типа лиганда на основе XGBoost."""
    
    def __init__(self, device: str = None):
        """
        Инициализация классификатора лигандов.
        
        Args:
            device (str, optional): Устройство для вычислений (не используется для XGBoost)
        """
        super().__init__(
            model_path=str(MODEL_CONFIG['ligand_classifier']['path']),
            device=device
        )
        
        # Загрузка скейлера
        self.scaler = joblib.load(SCALER_CONFIG['ligand'])
        self.label_encoder = joblib.load('saved_scalers/label_encoder_ligand.pkl')
        
    def load_model(self) -> None:
        """Загрузка модели из файла."""
        try:
            self.model = xgb.Booster()
            self.model.load_model(self.model_path)
            logger.info("Модель классификации лигандов успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {str(e)}")
            raise
    
    def preprocess_input(self, input_data: Dict[str, Any]) -> np.ndarray:
        """
        Предобработка входных данных.
        
        Args:
            input_data: Словарь с входными параметрами
            
        Returns:
            np.ndarray: Подготовленные данные для модели
        """
        try:
            # Преобразуем входные данные в numpy массив
            features = np.array(list(input_data.values())).reshape(1, -1)
            
            # Нормализуем данные
            scaled_features = self.scaler.transform(features)
            
            # Преобразуем в формат DMatrix для XGBoost
            return xgb.DMatrix(scaled_features)
        except Exception as e:
            logger.error(f"Ошибка при предобработке данных: {str(e)}")
            raise
    
    def predict(self, input_data: xgb.DMatrix) -> np.ndarray:
        """
        Выполнение предсказания.
        
        Args:
            input_data: Данные в формате DMatrix
            
        Returns:
            np.ndarray: Массив с вероятностями классов
        """
        try:
            return self.model.predict(input_data)
        except Exception as e:
            logger.error(f"Ошибка при выполнении предсказания: {str(e)}")
            raise
    
    def postprocess_output(self, predictions: np.ndarray) -> Dict[str, Any]:
        """
        Постобработка выходных данных.
        
        Args:
            predictions: Массив с предсказаниями
            
        Returns:
            Dict[str, Any]: Словарь с результатами предсказания
        """
        try:
            # Получаем индекс класса с максимальной вероятностью
            class_idx = np.argmax(predictions[0])
            confidence = float(predictions[0][class_idx])
            
            # Преобразуем индекс в название лиганда
            ligand_type = self.label_encoder.inverse_transform([class_idx])[0]
            
            return {
                'ligand_type': ligand_type,
                'confidence': confidence,
                'all_probabilities': {
                    ligand: float(prob)
                    for ligand, prob in zip(self.label_encoder.classes_, predictions[0])
                }
            }
        except Exception as e:
            logger.error(f"Ошибка при постобработке результатов: {str(e)}")
            raise 