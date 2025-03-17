from abc import ABC, abstractmethod
import torch
import logging
from typing import Any, Dict, Optional, List, Tuple
from ..utils.cache import create_cache_key, cached_prediction
from ..utils.performance.batch_processing import BatchProcessor
from ..utils.performance.quantization import ModelQuantizer
from ..utils.performance.cuda_optimization import CUDAOptimizer
from ..utils.performance.profiling import ModelProfiler
from ..utils.performance.pruning import ModelPruner

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    """Базовый класс для всех моделей в проекте."""
    
    def __init__(
        self,
        model_path: str,
        device: Optional[str] = None,
        use_cache: bool = True,
        batch_size: int = 32,
        use_quantization: bool = False,
        enable_profiling: bool = False,
        enable_pruning: bool = False,
        pruning_amount: float = 0.3,
        pruning_method: str = "l1_unstructured"
    ):
        """
        Инициализация базовой модели.
        
        Args:
            model_path: Путь к файлу модели
            device: Устройство для вычислений (cuda/cpu)
            use_cache: Использовать ли кэширование
            batch_size: Размер пакета для пакетной обработки
            use_quantization: Использовать ли квантизацию модели
            enable_profiling: Включить ли профилирование
            enable_pruning: Включить ли прунинг
            pruning_amount: Доля параметров для удаления при прунинге
            pruning_method: Метод прунинга
        """
        self.model_path = model_path
        self.use_cache = use_cache
        self.use_quantization = use_quantization
        self.enable_profiling = enable_profiling
        self.enable_pruning = enable_pruning
        
        # Оптимизация CUDA
        if device is None:
            self.device = CUDAOptimizer.get_optimal_device()
        else:
            self.device = torch.device(device)
        
        if self.device.type == 'cuda':
            CUDAOptimizer.optimize_cuda_memory()
            CUDAOptimizer.enable_cudnn_autotuner()
        
        self.model = None
        self.batch_processor = BatchProcessor(batch_size=batch_size)
        
        # Инициализация профилировщика
        if self.enable_profiling:
            self.profiler = ModelProfiler()
            
        # Инициализация прунера
        if self.enable_pruning:
            self.pruner = ModelPruner(
                amount=pruning_amount,
                pruning_method=pruning_method
            )
        
        logger.info(f"Инициализация модели из {model_path} на устройстве {self.device}")
    
    def _optimize_model(self, model: torch.nn.Module) -> torch.nn.Module:
        """
        Применяет оптимизации к модели.
        
        Args:
            model: Исходная модель
            
        Returns:
            torch.nn.Module: Оптимизированная модель
        """
        if self.use_quantization and self.device.type == 'cpu':
            model = ModelQuantizer.quantize_dynamic(model)
            
        if self.enable_pruning:
            pruning_results = self.pruner.prune_model(model)
            self.pruner.print_summary(pruning_results)
            
        return model
    
    @abstractmethod
    def load_model(self) -> None:
        """Загрузка модели из файла."""
        pass
    
    @abstractmethod
    def preprocess_input(self, input_data: Dict[str, Any]) -> torch.Tensor:
        """
        Предобработка входных данных.
        
        Args:
            input_data: Входные данные
            
        Returns:
            torch.Tensor: Предобработанные данные
        """
        pass
    
    @abstractmethod
    def predict(self, input_tensor: torch.Tensor) -> torch.Tensor:
        """
        Выполнение предсказания.
        
        Args:
            input_tensor: Входной тензор
            
        Returns:
            torch.Tensor: Результат предсказания
        """
        pass
    
    @abstractmethod
    def postprocess_output(self, predictions: torch.Tensor) -> Dict[str, Any]:
        """
        Постобработка выходных данных.
        
        Args:
            predictions: Предсказания модели
            
        Returns:
            Dict[str, Any]: Обработанный результат
        """
        pass
    
    def process_single(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработка одного элемента данных.
        
        Args:
            input_data: Входные данные
            
        Returns:
            Dict[str, Any]: Результат предсказания
        """
        if self.use_cache:
            cache_key = create_cache_key(input_data)
            cached_result = cached_prediction(cache_key, self.__class__.__name__)
            if cached_result is not None:
                return cached_result
        
        # Загружаем модель при первом использовании
        if self.model is None:
            self.load_model()
            self.model = self._optimize_model(self.model)
        
        # Выполняем предсказание
        input_tensor = self.preprocess_input(input_data)
        predictions = self.predict(input_tensor)
        result = self.postprocess_output(predictions)
        
        # Сохраняем в кэш
        if self.use_cache:
            cached_prediction.cache_info = result
            
        return result
    
    def process_batch(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Пакетная обработка данных.
        
        Args:
            batch_data: Список входных данных
            
        Returns:
            List[Dict[str, Any]]: Список результатов предсказаний
        """
        return self.batch_processor.process_all(batch_data, self.process_single)
    
    def get_memory_stats(self) -> Tuple[int, int, int]:
        """
        Получает статистику использования памяти.
        
        Returns:
            Tuple[int, int, int]: (всего памяти, использовано памяти, свободно памяти)
        """
        return CUDAOptimizer.get_memory_stats(self.device)

    def __call__(self, input_data: Any) -> Any:
        """
        Выполнение полного пайплайна предсказания.
        
        Args:
            input_data: Входные данные
            
        Returns:
            Результат предсказания
        """
        try:
            if self.model is None:
                self.load_model()
            
            preprocessed_data = self.preprocess_input(input_data)
            predictions = self.predict(preprocessed_data)
            result = self.postprocess_output(predictions)
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при выполнении предсказания: {str(e)}")
            raise

    def profile_inference(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Профилирование процесса предсказания.
        
        Args:
            input_data: Входные данные
            
        Returns:
            Dict[str, Any]: Результаты профилирования
        """
        if not self.enable_profiling:
            logger.warning("Профилирование отключено")
            return {}
            
        if self.model is None:
            self.load_model()
            self.model = self._optimize_model(self.model)
            
        results = self.profiler.profile_model(self, input_data)
        self.profiler.print_summary(results)
        return results
    
    def create_trace(self, input_data: Dict[str, Any], trace_file: str) -> None:
        """
        Создает trace-файл для анализа производительности.
        
        Args:
            input_data: Входные данные
            trace_file: Путь для сохранения trace-файла
        """
        if not self.enable_profiling:
            logger.warning("Профилирование отключено")
            return
            
        if self.model is None:
            self.load_model()
            self.model = self._optimize_model(self.model)
            
        self.profiler.analyze_trace(self, input_data, trace_file)

    def analyze_model_parameters(self) -> Dict[str, Any]:
        """
        Анализирует параметры модели.
        
        Returns:
            Dict[str, Any]: Статистика модели
        """
        if self.model is None:
            self.load_model()
            self.model = self._optimize_model(self.model)
            
        if self.enable_pruning:
            return self.pruner.analyze_model(self.model)
        return {} 