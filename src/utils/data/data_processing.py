import numpy as np
import pandas as pd
from typing import Dict, Any, Union, Tuple
from ...config import CALCULATION_CONSTANTS, VALIDATION_RULES
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Исключение для ошибок валидации данных."""
    pass

def validate_input_parameters(parameters: Dict[str, float]) -> None:
    """
    Валидация входных параметров.
    
    Args:
        parameters: Словарь с входными параметрами
        
    Raises:
        ValidationError: Если параметры не проходят валидацию
    """
    for param_name, value in parameters.items():
        if param_name in VALIDATION_RULES:
            rules = VALIDATION_RULES[param_name]
            if value < rules['min'] or value > rules['max']:
                raise ValidationError(
                    f"Параметр {param_name} должен быть в диапазоне "
                    f"[{rules['min']}, {rules['max']}]"
                )

def calculate_derived_parameters(
    SBAT_m2_gr: float,
    a0_mmoll_gr: float,
    E_kDg_moll: float,
    Ws_cm3_gr: float,
    Sme_m2_gr: float
) -> Dict[str, float]:
    """
    Рассчитывает производные параметры на основе входных данных.
    
    Args:
        SBAT_m2_gr: Удельная площадь поверхности (м2/г)
        a0_mmoll_gr: Предельная адсорбция (ммоль/г)
        E_kDg_moll: Энергия адсорбции азота (кДж/моль)
        Ws_cm3_gr: Общий объем пор (см3/г)
        Sme_m2_gr: Площадь поверхности мезопор (м2/г)
        
    Returns:
        Dict[str, float]: Словарь с рассчитанными параметрами
    """
    # Объем микропор
    W0_cm3_g = 0.034692 * a0_mmoll_gr
    
    # Энергия адсорбции по бензолу
    E0_KDG_moll = E_kDg_moll / 0.33 if E_kDg_moll > 0 else 1e-6
    
    # Полуширина пор
    x0_nm = 12 / E0_KDG_moll
    
    # Объем мезопор
    Wme_cm3_gr = Ws_cm3_gr - W0_cm3_g
    
    return {
        'W0_cm3_g': W0_cm3_g,
        'E0_KDG_moll': E0_KDG_moll,
        'x0_nm': x0_nm,
        'Wme_cm3_gr': Wme_cm3_gr
    }

def normalize_features(
    features: np.ndarray,
    scaler: Any
) -> np.ndarray:
    """
    Нормализация признаков с помощью переданного скейлера.
    
    Args:
        features: Массив признаков
        scaler: Объект скейлера
        
    Returns:
        np.ndarray: Нормализованные признаки
    """
    try:
        return scaler.transform(features)
    except Exception as e:
        logger.error(f"Ошибка при нормализации признаков: {str(e)}")
        raise

def prepare_features(
    input_data: Dict[str, float],
    features_list: list,
    scaler: Any
) -> np.ndarray:
    """
    Подготавливает признаки для модели.
    
    Args:
        input_data: Словарь с входными данными
        features_list: Список признаков в нужном порядке
        scaler: Обученный скейлер
        
    Returns:
        np.ndarray: Подготовленные признаки
    """
    # Создаем DataFrame с одной строкой
    df = pd.DataFrame([input_data])
    
    # Выбираем только нужные признаки в правильном порядке
    features = df[features_list].values
    
    # Нормализуем признаки
    features_scaled = scaler.transform(features)
    
    return features_scaled

def process_model_output(
    output: np.ndarray,
    label_encoder: Any,
    top_k: int = 3
) -> Tuple[str, float, list]:
    """
    Обрабатывает выход модели.
    
    Args:
        output: Выход модели (вероятности классов)
        label_encoder: Энкодер меток
        top_k: Количество лучших предсказаний
        
    Returns:
        Tuple[str, float, list]: (лучший класс, его вероятность, список топ-k предсказаний)
    """
    # Получаем вероятности
    probabilities = output.flatten()
    
    # Находим индексы top_k лучших предсказаний
    top_indices = np.argsort(probabilities)[-top_k:][::-1]
    
    # Получаем классы и их вероятности
    predictions = [
        (label_encoder.inverse_transform([idx])[0], float(probabilities[idx]))
        for idx in top_indices
    ]
    
    # Возвращаем лучший класс, его вероятность и все топ предсказания
    return predictions[0][0], predictions[0][1], predictions 