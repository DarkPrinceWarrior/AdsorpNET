import torch
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class CUDAOptimizer:
    """Класс для оптимизации работы с CUDA."""
    
    @staticmethod
    def get_optimal_device() -> torch.device:
        """
        Определяет оптимальное устройство для вычислений.
        
        Returns:
            torch.device: Оптимальное устройство
        """
        if torch.cuda.is_available():
            # Выбираем GPU с наибольшим объемом свободной памяти
            device_count = torch.cuda.device_count()
            if device_count > 1:
                max_free_memory = 0
                optimal_device = 0
                
                for i in range(device_count):
                    torch.cuda.set_device(i)
                    torch.cuda.empty_cache()
                    free_memory = torch.cuda.get_device_properties(i).total_memory - torch.cuda.memory_allocated(i)
                    if free_memory > max_free_memory:
                        max_free_memory = free_memory
                        optimal_device = i
                
                return torch.device(f'cuda:{optimal_device}')
            return torch.device('cuda:0')
        return torch.device('cpu')
    
    @staticmethod
    def optimize_cuda_memory() -> None:
        """Оптимизирует использование памяти CUDA."""
        if torch.cuda.is_available():
            # Очищаем кэш CUDA
            torch.cuda.empty_cache()
            # Включаем оптимизацию памяти
            torch.cuda.set_per_process_memory_fraction(0.8)  # Используем 80% доступной памяти
    
    @staticmethod
    def get_memory_stats(device: Optional[torch.device] = None) -> Tuple[int, int, int]:
        """
        Получает статистику использования памяти.
        
        Args:
            device: Устройство для проверки
            
        Returns:
            Tuple[int, int, int]: (всего памяти, использовано памяти, свободно памяти)
        """
        if device is None:
            device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
            
        if device.type == 'cuda':
            total = torch.cuda.get_device_properties(device).total_memory
            allocated = torch.cuda.memory_allocated(device)
            free = total - allocated
            return total, allocated, free
        return 0, 0, 0  # Для CPU
    
    @staticmethod
    def enable_cudnn_autotuner() -> None:
        """Включает автонастройку cuDNN."""
        if torch.cuda.is_available():
            torch.backends.cudnn.benchmark = True
            logger.info("cuDNN autotuner включен") 