"""
Сервис для загрузки и управления моделями.
Реализует паттерны Singleton и Registry для эффективного управления моделями.
"""

import torch
import xgboost as xgb
import joblib
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Type, Union
from functools import lru_cache

from src.config.model_config import MODELS_DIR, SCALERS_DIR
from src.domain import (
    features_metal, features_ligand, features_solvent,
    features_Tsyn, features_Tdry, features_Treg
)

logger = logging.getLogger(__name__)

class ModelService:
    """
    Сервис для управления моделями машинного обучения.
    Реализует ленивую загрузку и кэширование моделей.
    """
    
    _instance = None  # Синглтон-инстанс
    
    def __new__(cls):
        """Реализация паттерна Singleton."""
        if cls._instance is None:
            cls._instance = super(ModelService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Инициализация сервиса моделей."""
        if self._initialized:
            return
            
        self._models = {}
        self._encoders = {}
        self._scalers = {}
        
        # Принудительно используем CPU для совместимости
        self._device = torch.device('cpu')
        
        self._initialized = True
        logger.info(f"Инициализирован сервис моделей (устройство: {self._device})")
        
    def get_device(self) -> torch.device:
        """Возвращает устройство, используемое для моделей."""
        return self._device
    
    def _load_torch_model(
        self, 
        model_class: Type, 
        model_path: str, 
        input_dim: int,
        num_classes: Optional[int] = None
    ) -> torch.nn.Module:
        """
        Загружает модель PyTorch.
        
        Args:
            model_class: Класс модели
            model_path: Путь к файлу модели
            input_dim: Размерность входных данных
            num_classes: Количество классов (для классификаторов)
            
        Returns:
            torch.nn.Module: Загруженная модель
        """
        if num_classes is not None:
            model = model_class(input_dim=input_dim, num_classes=num_classes)
        else:
            model = model_class(input_dim=input_dim)
        
        model.load_state_dict(
            torch.load(
                model_path,
                map_location=self._device,  # Используем устройство из экземпляра
                weights_only=True
            )
        )
        model = model.to(self._device)  # Гарантируем, что модель на правильном устройстве
        model.eval()
        logger.info(f"Загружена PyTorch модель: {model_path}")
        return model
    
    def _load_xgb_model(self, model_path: str) -> xgb.Booster:
        """
        Загружает модель XGBoost.
        
        Args:
            model_path: Путь к файлу модели
            
        Returns:
            xgb.Booster: Загруженная модель
        """
        model = xgb.Booster()
        model.load_model(model_path)
        logger.info(f"Загружена XGBoost модель: {model_path}")
        return model
    
    def _load_scaler(self, scaler_path: str) -> Any:
        """
        Загружает sklearn скейлер.
        
        Args:
            scaler_path: Путь к файлу скейлера
            
        Returns:
            Any: Загруженный скейлер
        """
        scaler = joblib.load(scaler_path)
        logger.info(f"Загружен скейлер: {scaler_path}")
        return scaler
    
    def _load_encoder(self, encoder_path: str) -> Any:
        """
        Загружает sklearn энкодер.
        
        Args:
            encoder_path: Путь к файлу энкодера
            
        Returns:
            Any: Загруженный энкодер
        """
        encoder = joblib.load(encoder_path)
        logger.info(f"Загружен энкодер: {encoder_path}")
        return encoder
    
    @lru_cache(maxsize=None)
    def get_model(self, model_name: str) -> Any:
        """
        Получает модель по имени. Реализует ленивую загрузку.
        
        Args:
            model_name: Имя модели
            
        Returns:
            Any: Загруженная модель
            
        Raises:
            ValueError: Если модель с указанным именем не найдена
        """
        if model_name in self._models:
            return self._models[model_name]
            
        # Загрузка моделей по запросу
        from saved_models.models_list import (
            MetalClassifier, TransformerClassifier,
            TransformerTsynClassifier, TransformerTdryClassifier,
            TransformerTregClassifier
        )
        
        # Получаем сначала необходимые энкодеры, если нужны
        if model_name.startswith('major_metal') and 'label_encoder_major_metal' not in self._encoders:
            self._encoders['label_encoder_major_metal'] = self._load_encoder(
                SCALERS_DIR / 'label_encoder_major_metal.pkl'
            )
        elif model_name.startswith('minor_metal') and 'label_encoder_minor_metal' not in self._encoders:
            self._encoders['label_encoder_minor_metal'] = self._load_encoder(
                SCALERS_DIR / 'label_encoder_minor_metal.pkl'
            )
        elif model_name.startswith('Tsyn') and 'label_encoder_Tsyn' not in self._encoders:
            self._encoders['label_encoder_Tsyn'] = self._load_encoder(
                SCALERS_DIR / 'label_encoder_Tsyn.pkl'
            )
        elif model_name.startswith('Tdry') and 'label_encoder_Tdry' not in self._encoders:
            self._encoders['label_encoder_Tdry'] = self._load_encoder(
                SCALERS_DIR / 'label_encoder_Tdry.pkl'
            )
        elif model_name.startswith('Treg') and 'label_encoder_Treg' not in self._encoders:
            self._encoders['label_encoder_Treg'] = self._load_encoder(
                SCALERS_DIR / 'label_encoder_Treg.pkl'
            )
        
        # Загрузка модели в зависимости от имени
        if model_name == 'metal_binary':
            model = self._load_torch_model(
                MetalClassifier,
                MODELS_DIR / 'dnn_metal_binary_classifier.pth',
                len(features_metal)
            )
        elif model_name == 'major_metal':
            model = self._load_torch_model(
                TransformerClassifier,
                MODELS_DIR / 'best_major_classifier_metal.pth',
                len(features_metal),
                len(self._encoders['label_encoder_major_metal'].classes_)
            )
        elif model_name == 'minor_metal':
            model = self._load_torch_model(
                TransformerClassifier,
                MODELS_DIR / 'best_minor_classifier_metal.pth',
                len(features_metal),
                len(self._encoders['label_encoder_minor_metal'].classes_)
            )
        elif model_name == 'ligand':
            model = self._load_xgb_model(MODELS_DIR / 'xgb_ligand_classifier.json')
        elif model_name == 'solvent':
            model = self._load_xgb_model(MODELS_DIR / 'xgb_solvent_classifier.json')
        elif model_name == 'salt_mass':
            model = self._load_xgb_model(MODELS_DIR / 'xgb_mass_salt_classifier.json')
        elif model_name == 'acid_mass':
            model = self._load_xgb_model(MODELS_DIR / 'xgb_acid_mass_regressor.json')
        elif model_name == 'Vsyn':
            model = self._load_xgb_model(MODELS_DIR / 'model_xgb_V_syn_regressor.json')
        elif model_name == 'Tsyn':
            model = self._load_torch_model(
                TransformerTsynClassifier,
                MODELS_DIR / 'model_Tsyn.pth',
                len(features_Tsyn),
                len(self._encoders['label_encoder_Tsyn'].classes_)
            )
        elif model_name == 'Tdry':
            model = self._load_torch_model(
                TransformerTdryClassifier,
                MODELS_DIR / 'model_Tdry.pth',
                len(features_Tdry),
                len(self._encoders['label_encoder_Tdry'].classes_)
            )
        elif model_name == 'Treg':
            model = self._load_torch_model(
                TransformerTregClassifier,
                MODELS_DIR / 'model_Treg.pth',
                len(features_Treg),
                len(self._encoders['label_encoder_Treg'].classes_)
            )
        else:
            raise ValueError(f"Неизвестная модель: {model_name}")
        
        self._models[model_name] = model
        return model
    
    @lru_cache(maxsize=None)
    def get_scaler(self, scaler_name: str) -> Any:
        """
        Получает скейлер по имени. Реализует ленивую загрузку.
        
        Args:
            scaler_name: Имя скейлера
            
        Returns:
            Any: Загруженный скейлер
            
        Raises:
            ValueError: Если скейлер с указанным именем не найден
        """
        if scaler_name in self._scalers:
            return self._scalers[scaler_name]
            
        scaler_mapping = {
            'binary_metals': 'scaler_binary_metals.pkl',
            'major_metal': 'scaler_major_metal.pkl',
            'minor_metal': 'scaler_minor_metal.pkl',
            'ligand': 'scaler_ligand.pkl',
            'solvent': 'scaler_solvent.pkl',
            'salt_mass': 'scaler_salt_mass.pkl',
            'acid_mass': 'scaler_acid_mass.pkl',
            'Vsyn': 'scaler_Vsyn.pkl',
            'Tsyn': 'scaler_Tsyn.pkl',
            'Tdry': 'scaler_Tdry.pkl',
            'Treg': 'scaler_Treg.pkl'
        }
        
        if scaler_name not in scaler_mapping:
            raise ValueError(f"Неизвестный скейлер: {scaler_name}")
            
        scaler_path = SCALERS_DIR / scaler_mapping[scaler_name]
        scaler = self._load_scaler(scaler_path)
        self._scalers[scaler_name] = scaler
        
        return scaler
    
    @lru_cache(maxsize=None)
    def get_encoder(self, encoder_name: str) -> Any:
        """
        Получает энкодер по имени. Реализует ленивую загрузку.
        
        Args:
            encoder_name: Имя энкодера
            
        Returns:
            Any: Загруженный энкодер
            
        Raises:
            ValueError: Если энкодер с указанным именем не найден
        """
        if encoder_name in self._encoders:
            return self._encoders[encoder_name]
            
        encoder_mapping = {
            'major_metal': 'label_encoder_major_metal.pkl',
            'minor_metal': 'label_encoder_minor_metal.pkl',
            'ligand': 'label_encoder_ligand.pkl',
            'solvent': 'label_encoder_solvent.pkl',
            'Tsyn': 'label_encoder_Tsyn.pkl',
            'Tdry': 'label_encoder_Tdry.pkl',
            'Treg': 'label_encoder_Treg.pkl'
        }
        
        if encoder_name not in encoder_mapping:
            raise ValueError(f"Неизвестный энкодер: {encoder_name}")
            
        encoder_path = SCALERS_DIR / encoder_mapping[encoder_name]
        encoder = self._load_encoder(encoder_path)
        self._encoders[encoder_name] = encoder
        
        return encoder
    
    def get_all_models(self) -> Dict[str, Any]:
        """
        Загружает все модели.
        
        Returns:
            Dict[str, Any]: Словарь с загруженными моделями
        """
        # Перечень всех доступных моделей
        model_names = [
            'metal_binary', 'major_metal', 'minor_metal',
            'ligand', 'solvent', 'salt_mass', 'acid_mass',
            'Vsyn', 'Tsyn', 'Tdry', 'Treg'
        ]
        
        # Загружаем все модели
        for name in model_names:
            if name not in self._models:
                self.get_model(name)
                
        return self._models
    
    def get_all_scalers(self) -> Dict[str, Any]:
        """
        Загружает все скейлеры.
        
        Returns:
            Dict[str, Any]: Словарь с загруженными скейлерами
        """
        # Перечень всех доступных скейлеров
        scaler_names = [
            'binary_metals', 'major_metal', 'minor_metal',
            'ligand', 'solvent', 'salt_mass', 'acid_mass',
            'Vsyn', 'Tsyn', 'Tdry', 'Treg'
        ]
        
        # Загружаем все скейлеры
        for name in scaler_names:
            if name not in self._scalers:
                self.get_scaler(name)
                
        return self._scalers
    
    def get_all_encoders(self) -> Dict[str, Any]:
        """
        Загружает все энкодеры.
        
        Returns:
            Dict[str, Any]: Словарь с загруженными энкодерами
        """
        # Перечень всех доступных энкодеров
        encoder_names = [
            'major_metal', 'minor_metal', 'ligand', 'solvent',
            'Tsyn', 'Tdry', 'Treg'
        ]
        
        # Загружаем все энкодеры
        for name in encoder_names:
            if name not in self._encoders:
                self.get_encoder(name)
                
        return self._encoders
    
    def clear_cache(self) -> None:
        """Очищает кэш моделей, скейлеров и энкодеров."""
        self._models = {}
        self._scalers = {}
        self._encoders = {}
        
        # Очищаем также кэш декораторов
        self.get_model.cache_clear()
        self.get_scaler.cache_clear()
        self.get_encoder.cache_clear()
        
        logger.info("Кэш моделей очищен")
        
    # Добавим эти методы в класс ModelService в src/services/model_service.py

    def unload_unused_models(self, keep_models: list = None) -> None:
        """
        Выгружает неиспользуемые модели из памяти для экономии ресурсов.
        
        Args:
            keep_models: Список имен моделей, которые нужно оставить в памяти
        """
        if keep_models is None:
            keep_models = []
            
        # Определяем модели для выгрузки
        models_to_unload = [name for name in self._models.keys() if name not in keep_models]
        
        # Выгружаем модели
        for model_name in models_to_unload:
            self._models.pop(model_name, None)
            logger.info(f"Модель {model_name} выгружена из памяти")
        
        # Очищаем кэш декораторов
        self.get_model.cache_clear()
        
        # Запускаем сборщик мусора
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        logger.info(f"Выгружено {len(models_to_unload)} моделей, оставлено {len(keep_models)}")

    def preload_models(self, model_names: list) -> None:
        """
        Предварительно загружает указанные модели в память.
        
        Args:
            model_names: Список имен моделей для предзагрузки
        """
        for model_name in model_names:
            try:
                if model_name not in self._models:
                    logger.info(f"Предзагрузка модели {model_name}")
                    self.get_model(model_name)
            except Exception as e:
                logger.error(f"Ошибка при предзагрузке модели {model_name}: {str(e)}")

    def get_loaded_models(self) -> list:
        """
        Возвращает список загруженных моделей.
        
        Returns:
            list: Имена загруженных моделей
        """
        return list(self._models.keys())

    def get_model_memory_usage(self) -> Dict[str, float]:
        """
        Оценивает использование памяти каждой загруженной моделью.
        
        Returns:
            Dict[str, float]: Словарь {имя_модели: размер_в_МБ}
        """
        memory_usage = {}
        
        for name, model in self._models.items():
            try:
                # Для PyTorch моделей
                if hasattr(model, 'parameters'):
                    params_size = sum(p.numel() * p.element_size() for p in model.parameters()) / (1024 * 1024)
                    buffers_size = sum(b.numel() * b.element_size() for b in model.buffers()) / (1024 * 1024)
                    memory_usage[name] = params_size + buffers_size
                # Для других типов моделей (XGBoost и т.д.)
                else:
                    import sys
                    memory_usage[name] = sys.getsizeof(model) / (1024 * 1024)
            except Exception as e:
                logger.warning(f"Не удалось определить размер модели {name}: {str(e)}")
                memory_usage[name] = 0.0
        
        return memory_usage