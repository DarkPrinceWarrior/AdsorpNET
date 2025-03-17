import torch
from typing import List, Dict, Any, Callable
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from ...config import MODEL_CONFIG

class BatchProcessor:
    """Класс для пакетной обработки данных."""
    
    def __init__(self, batch_size: int = 32, max_workers: int = 4):
        """
        Инициализация процессора пакетной обработки.
        
        Args:
            batch_size: Размер пакета
            max_workers: Максимальное количество параллельных потоков
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
    
    def create_batches(self, data: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Разделяет данные на пакеты.
        
        Args:
            data: Список словарей с входными данными
            
        Returns:
            List[List[Dict[str, Any]]]: Список пакетов данных
        """
        return [
            data[i:i + self.batch_size]
            for i in range(0, len(data), self.batch_size)
        ]
    
    def process_batch(
        self,
        batch: List[Dict[str, Any]],
        process_fn: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Обрабатывает один пакет данных.
        
        Args:
            batch: Пакет данных
            process_fn: Функция обработки одного элемента
            
        Returns:
            List[Dict[str, Any]]: Результаты обработки пакета
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(process_fn, batch))
    
    def process_all(
        self,
        data: List[Dict[str, Any]],
        process_fn: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Обрабатывает все данные пакетами.
        
        Args:
            data: Список входных данных
            process_fn: Функция обработки одного элемента
            
        Returns:
            List[Dict[str, Any]]: Результаты обработки всех данных
        """
        batches = self.create_batches(data)
        results = []
        
        for batch in batches:
            batch_results = self.process_batch(batch, process_fn)
            results.extend(batch_results)
        
        return results 