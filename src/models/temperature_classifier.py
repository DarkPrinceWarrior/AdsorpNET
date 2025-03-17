import torch
import torch.nn as nn
import numpy as np
import logging
from typing import Dict, Any, List
from .base_model import BaseModel
from ..config import MODEL_CONFIG, SCALER_CONFIG
import joblib

logger = logging.getLogger(__name__)

class TemperatureNet(nn.Module):
    """Базовая архитектура нейронной сети для классификации температур."""
    
    def __init__(self, input_dim: int, hidden_dim: int = 128, num_classes: int = 5):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.BatchNorm1d(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.BatchNorm1d(hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class BaseTemperatureClassifier(BaseModel):
    """Базовый класс для классификации температур."""
    
    def __init__(self, temp_type: str, device: str = None):
        """
        Инициализация классификатора температур.
        
        Args:
            temp_type (str): Тип температуры ('Tsyn', 'Tdry', 'Treg')
            device (str, optional): Устройство для вычислений
        """
        self.temp_type = temp_type
        model_key = f'model_{temp_type.lower()}'
        
        super().__init__(
            model_path=str(MODEL_CONFIG[model_key]['path']),
            device=device
        )
        
        # Загрузка скейлера и энкодера
        self.scaler = joblib.load(SCALER_CONFIG[temp_type.lower()])
        self.label_encoder = joblib.load(f'saved_scalers/label_encoder_{temp_type}.pkl')
        self.input_features = None
        
    def load_model(self) -> None:
        """Загрузка модели из файла."""
        try:
            # Определяем размерность входа на основе скейлера
            self.input_features = self.scaler.n_features_in_
            
            # Создаем модель с правильной размерностью
            self.model = TemperatureNet(
                input_dim=self.input_features,
                num_classes=len(self.label_encoder.classes_)
            )
            
            # Загружаем веса
            self.model.load_state_dict(
                torch.load(self.model_path, map_location=self.device)
            )
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Модель классификации {self.temp_type} успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка при загрузке модели: {str(e)}")
            raise
    
    def preprocess_input(self, input_data: Dict[str, Any]) -> torch.Tensor:
        """
        Предобработка входных данных.
        
        Args:
            input_data: Словарь с входными параметрами
            
        Returns:
            torch.Tensor: Подготовленный тензор для модели
        """
        try:
            # Преобразуем входные данные в numpy массив
            features = np.array(list(input_data.values())).reshape(1, -1)
            
            # Нормализуем данные
            scaled_features = self.scaler.transform(features)
            
            # Преобразуем в тензор PyTorch
            return torch.FloatTensor(scaled_features).to(self.device)
        except Exception as e:
            logger.error(f"Ошибка при предобработке данных: {str(e)}")
            raise
    
    def predict(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """
        Выполнение предсказания.
        
        Args:
            input_tensor: Входной тензор
            
        Returns:
            torch.Tensor: Тензор с предсказаниями
        """
        try:
            with torch.no_grad():
                outputs = self.model(input_tensor)
                return torch.softmax(outputs, dim=1)
        except Exception as e:
            logger.error(f"Ошибка при выполнении предсказания: {str(e)}")
            raise
    
    def postprocess_output(self, predictions: torch.Tensor) -> Dict[str, Any]:
        """
        Постобработка выходных данных.
        
        Args:
            predictions: Тензор с предсказаниями
            
        Returns:
            Dict[str, Any]: Словарь с результатами предсказания
        """
        try:
            predictions_np = predictions.cpu().numpy()
            
            # Получаем индекс класса с максимальной вероятностью
            class_idx = np.argmax(predictions_np[0])
            confidence = float(predictions_np[0][class_idx])
            
            # Преобразуем индекс в значение температуры
            temperature = self.label_encoder.inverse_transform([class_idx])[0]
            
            # Формируем словарь с вероятностями для всех классов
            probabilities = {
                str(temp): float(prob)
                for temp, prob in zip(self.label_encoder.classes_, predictions_np[0])
            }
            
            # Сортируем температуры по убыванию вероятности
            sorted_temps = sorted(
                probabilities.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            return {
                'temperature': temperature,
                'confidence': confidence,
                'all_probabilities': probabilities,
                'top_3_temperatures': [
                    {'value': temp, 'probability': prob}
                    for temp, prob in sorted_temps[:3]
                ]
            }
        except Exception as e:
            logger.error(f"Ошибка при постобработке результатов: {str(e)}")
            raise 