import torch
from torch.profiler import profile, record_function, ProfilerActivity
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelProfiler:
    """Класс для профилирования моделей."""
    
    def __init__(
        self,
        activities: Optional[List[ProfilerActivity]] = None,
        profile_memory: bool = True,
        with_stack: bool = True,
        output_dir: str = "profiling_results"
    ):
        """
        Инициализация профилировщика.
        
        Args:
            activities: Список активностей для профилирования
            profile_memory: Профилировать ли использование памяти
            with_stack: Включать ли информацию о стеке вызовов
            output_dir: Директория для сохранения результатов
        """
        self.activities = activities or [
            ProfilerActivity.CPU,
            ProfilerActivity.CUDA
        ]
        self.profile_memory = profile_memory
        self.with_stack = with_stack
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def profile_model(
        self,
        model: torch.nn.Module,
        input_data: Dict[str, Any],
        warm_up: int = 5,
        steps: int = 10
    ) -> Dict[str, Any]:
        """
        Профилирование модели.
        
        Args:
            model: Модель для профилирования
            input_data: Входные данные
            warm_up: Количество прогревочных итераций
            steps: Количество итераций для профилирования
            
        Returns:
            Dict[str, Any]: Результаты профилирования
        """
        results = {}
        
        with profile(
            activities=self.activities,
            profile_memory=self.profile_memory,
            with_stack=self.with_stack,
            record_shapes=True
        ) as prof:
            # Прогрев
            for _ in range(warm_up):
                with record_function("warm_up"):
                    _ = model(input_data)
            
            # Профилирование
            for _ in range(steps):
                with record_function("inference"):
                    _ = model(input_data)
        
        # Анализ результатов
        results["execution_time"] = {
            "avg_ms": prof.key_averages().total_average().cpu_time_total / 1000,
            "max_ms": max(e.cpu_time_total for e in prof.events()) / 1000
        }
        
        if self.profile_memory:
            results["memory"] = {
                "max_allocated_mb": torch.cuda.max_memory_allocated() / 1024**2,
                "max_reserved_mb": torch.cuda.max_memory_reserved() / 1024**2
            }
        
        # Анализ узких мест
        results["bottlenecks"] = []
        for event in prof.key_averages():
            if event.cpu_time_total > 1000:  # > 1ms
                results["bottlenecks"].append({
                    "name": event.key,
                    "cpu_time_ms": event.cpu_time_total / 1000,
                    "cuda_time_ms": event.cuda_time_total / 1000 if event.cuda_time_total else 0,
                    "memory_mb": event.cpu_memory_usage / 1024**2 if event.cpu_memory_usage else 0
                })
        
        # Сохранение результатов
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"profile_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
        
        logger.info(f"Результаты профилирования сохранены в {output_file}")
        return results
    
    @staticmethod
    def analyze_trace(
        model: torch.nn.Module,
        input_data: Dict[str, Any],
        trace_file: str
    ) -> None:
        """
        Создает trace-файл для анализа в Chrome Trace Viewer.
        
        Args:
            model: Модель для профилирования
            input_data: Входные данные
            trace_file: Путь для сохранения trace-файла
        """
        with profile(
            activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA],
            with_stack=True,
            record_shapes=True
        ) as prof:
            model(input_data)
        
        prof.export_chrome_trace(trace_file)
        logger.info(f"Trace-файл сохранен в {trace_file}")
    
    @staticmethod
    def print_summary(results: Dict[str, Any]) -> None:
        """
        Выводит сводку результатов профилирования.
        
        Args:
            results: Результаты профилирования
        """
        print("\n=== Результаты профилирования ===")
        print(f"Среднее время выполнения: {results['execution_time']['avg_ms']:.2f} мс")
        print(f"Максимальное время выполнения: {results['execution_time']['max_ms']:.2f} мс")
        
        if "memory" in results:
            print(f"\nИспользование памяти:")
            print(f"Максимально выделено: {results['memory']['max_allocated_mb']:.2f} МБ")
            print(f"Максимально зарезервировано: {results['memory']['max_reserved_mb']:.2f} МБ")
        
        if results["bottlenecks"]:
            print("\nУзкие места:")
            for b in results["bottlenecks"]:
                print(f"\nОперация: {b['name']}")
                print(f"CPU время: {b['cpu_time_ms']:.2f} мс")
                print(f"CUDA время: {b['cuda_time_ms']:.2f} мс")
                print(f"Использование памяти: {b['memory_mb']:.2f} МБ") 