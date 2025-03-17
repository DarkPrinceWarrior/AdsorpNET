import torch
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ModelQuantizer:
    """Класс для квантизации моделей PyTorch."""
    
    @staticmethod
    def quantize_dynamic(model: torch.nn.Module, dtype: Optional[torch.dtype] = torch.qint8) -> torch.nn.Module:
        """
        Применяет динамическую квантизацию к модели.
        
        Args:
            model: Исходная модель
            dtype: Тип данных для квантизации
            
        Returns:
            torch.nn.Module: Квантизированная модель
        """
        try:
            quantized_model = torch.quantization.quantize_dynamic(
                model,
                {torch.nn.Linear, torch.nn.Conv2d},
                dtype=dtype
            )
            logger.info("Модель успешно квантизирована")
            return quantized_model
        except Exception as e:
            logger.error(f"Ошибка при квантизации модели: {str(e)}")
            return model
    
    @staticmethod
    def prepare_static_quantization(model: torch.nn.Module) -> torch.nn.Module:
        """
        Подготавливает модель к статической квантизации.
        
        Args:
            model: Исходная модель
            
        Returns:
            torch.nn.Module: Подготовленная модель
        """
        model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
        model_prepared = torch.quantization.prepare(model)
        return model_prepared
    
    @staticmethod
    def quantize_static(model: torch.nn.Module) -> torch.nn.Module:
        """
        Применяет статическую квантизацию к подготовленной модели.
        
        Args:
            model: Подготовленная модель
            
        Returns:
            torch.nn.Module: Квантизированная модель
        """
        try:
            quantized_model = torch.quantization.convert(model)
            logger.info("Модель успешно квантизирована статически")
            return quantized_model
        except Exception as e:
            logger.error(f"Ошибка при статической квантизации: {str(e)}")
            return model 