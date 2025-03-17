# src/utils/storage/cache.py
"""
Модуль для кэширования результатов предсказаний моделей.
"""

import hashlib
import json
from functools import lru_cache
from typing import Dict, Any, Optional
import logging
import time

logger = logging.getLogger(__name__)

# Словарь для хранения времени жизни кэша для разных моделей (в секундах)
CACHE_TTL = {
    'default': 3600,  # 1 час по умолчанию
    'MetalClassifier': 7200,  # 2 часа
    'LigandClassifier': 7200,  # 2 часа 
    'SolventClassifier': 7200,  # 2 часа
    'TsynClassifier': 7200,  # 2 часа
    'TdryClassifier': 7200,  # 2 часа
    'TregClassifier': 7200,  # 2 часа
}

# Глобальный словарь для хранения времени последнего обновления кэша
_cache_timestamps = {}

def create_cache_key(input_data: Dict[str, Any]) -> str:
    """
    Создает уникальный ключ для кэширования на основе входных данных.
    
    Args:
        input_data: Словарь входных параметров
        
    Returns:
        str: Уникальный хеш-ключ
    """
    # Сортируем ключи для обеспечения консистентности
    sorted_items = sorted(input_data.items())
    # Создаем строку для хэширования
    cache_str = json.dumps(sorted_items)
    # Создаем хеш
    return hashlib.md5(cache_str.encode()).hexdigest()

@lru_cache(maxsize=1000)
def cached_prediction(cache_key: str, model_name: str) -> Optional[Dict[str, Any]]:
    """
    Получает кэшированный результат предсказания, учитывая TTL кэша.
    
    Args:
        cache_key: Ключ кэша
        model_name: Имя модели
        
    Returns:
        Optional[Dict[str, Any]]: Результат предсказания или None, если кэш устарел/отсутствует
    """
    # Проверяем время жизни кэша
    full_key = f"{model_name}:{cache_key}"
    current_time = time.time()
    
    if full_key in _cache_timestamps:
        last_update = _cache_timestamps[full_key]
        ttl = CACHE_TTL.get(model_name, CACHE_TTL['default'])
        
        # Если кэш устарел, возвращаем None
        if current_time - last_update > ttl:
            logger.debug(f"Кэш для {model_name} с ключом {cache_key[:8]} устарел")
            return None
            
    # Если кэша нет, возвращаем None
    if not hasattr(cached_prediction, 'cache_info'):
        return None
        
    # Записываем время обновления кэша
    _cache_timestamps[full_key] = current_time
    
    return cached_prediction.cache_info

def clear_prediction_cache():
    """Очищает кэш предсказаний."""
    cached_prediction.cache_clear()
    _cache_timestamps.clear()
    logger.info("Кэш предсказаний очищен")

def get_cache_stats() -> Dict[str, Any]:
    """
    Возвращает статистику использования кэша.
    
    Returns:
        Dict[str, Any]: Статистика кэша
    """
    cache_info = cached_prediction.cache_info()
    return {
        'hits': cache_info.hits,
        'misses': cache_info.misses,
        'maxsize': cache_info.maxsize,
        'currsize': cache_info.currsize,
        'cache_items': len(_cache_timestamps),
        'models_cached': len(set(k.split(':')[0] for k in _cache_timestamps.keys()))
    }