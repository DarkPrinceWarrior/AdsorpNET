import torch
import torch.nn as nn
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from .base_model import BaseModel
from ..config import MODEL_CONFIG, SCALER_CONFIG
import joblib

logger = logging.getLogger(__name__)

class MetalNet(nn.Module):
    """Нейронная сеть для классификации металлов."""
    
    def __init__(self, input_dim: int, num_classes: int = 2):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, num_classes)
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class MetalClassifier(BaseModel):
    """Классификатор для определения типа металла."""
    
    def __init__(self, model_type: str = 'binary', device: str = None):
        """
        Инициализация классификатора металлов.
        
        Args:
            model_type (str): Тип модели ('binary', 'major', 'minor')
            device (str, optional): Устройство для вычислений
        """
        self.model_type = model_type
        model_key = {
            'binary': 'metal_binary_classifier',
            'major': 'major_metal_classifier',
            'minor': 'minor_metal_classifier'
        }[model_type]
        
        super().__init__(
            model_path=str(MODEL_CONFIG[model_key]['path']),
            device=device
        )
        
        # Загрузка скейлера
        scaler_key = {
            'binary': 'binary_metals',
            'major': 'major_metal',
            'minor': 'minor_metal'
        }[model_type]
        
        self.scaler = joblib.load(SCALER_CONFIG[scaler_key])
        self.input_features = None  # Будет установлено при загрузке модели
        
    def load_model(self) -> None:
        """Загрузка модели из файла."""
        try:
            # Определяем размерность входа на основе скейлера
            self.input_features = self.scaler.n_features_in_
            
            # Создаем модель с правильной размерностью
            num_classes = 2 if self.model_type == 'binary' else {
                'major': 9,  # Количество основных металлов
                'minor': 9   # Количество второстепенных металлов
            }[self.model_type]
            
            self.model = MetalNet(self.input_features, num_classes)
            self.model.load_state_dict(
                torch.load(self.model_path, map_location=self.device)
            )
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Модель {self.model_type} успешно загружена")
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
                if self.model_type == 'binary':
                    predictions = torch.sigmoid(outputs)
                else:
                    predictions = torch.softmax(outputs, dim=1)
                return predictions
        except Exception as e:
            logger.error(f"Ошибка при выполнении предсказания: {str(e)}")
            raise
    
    def postprocess_output(self, output_tensor: torch.Tensor) -> Dict[str, Any]:
        """
        Постобработка выходных данных.
        
        Args:
            output_tensor: Тензор с предсказаниями
            
        Returns:
            Dict[str, Any]: Словарь с результатами предсказания
        """
        try:
            predictions = output_tensor.cpu().numpy()
            
            if self.model_type == 'binary':
                is_binary = predictions[0][0] > 0.5
                confidence = float(predictions[0][0])
                return {
                    'is_binary': bool(is_binary),
                    'confidence': confidence
                }
            else:
                class_idx = np.argmax(predictions[0])
                confidence = float(predictions[0][class_idx])
                metal_type = {
                    'major': ['Cu', 'Zn', 'Al', 'Fe', 'Zr', 'Mg', 'La', 'Ce', 'Y'],
                    'minor': ['Cu', 'Zn', 'Al', 'Fe', 'Zr', 'Mg', 'La', 'Ce', 'Y']
                }[self.model_type][class_idx]
                
                return {
                    'metal_type': metal_type,
                    'confidence': confidence
                }
        except Exception as e:
            logger.error(f"Ошибка при постобработке результатов: {str(e)}")
            raise 