import torch
import torch.nn.utils.prune as prune
from typing import Dict, Any, List, Union, Optional
import logging
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class ModelPruner:
    """Класс для прунинга моделей PyTorch."""
    
    def __init__(
        self,
        amount: float = 0.3,
        pruning_method: str = "l1_unstructured",
        save_dir: str = "pruning_results"
    ):
        """
        Инициализация прунера.
        
        Args:
            amount: Доля параметров для удаления (0.0 - 1.0)
            pruning_method: Метод прунинга ('l1_unstructured', 'random_unstructured')
            save_dir: Директория для сохранения результатов
        """
        self.amount = amount
        self.pruning_method = pruning_method
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        self._pruning_methods = {
            "l1_unstructured": prune.l1_unstructured,
            "random_unstructured": prune.random_unstructured
        }
    
    def _get_pruning_method(self):
        """Получает функцию прунинга по имени."""
        if self.pruning_method not in self._pruning_methods:
            raise ValueError(f"Неподдерживаемый метод прунинга: {self.pruning_method}")
        return self._pruning_methods[self.pruning_method]
    
    def analyze_model(self, model: torch.nn.Module) -> Dict[str, Any]:
        """
        Анализирует модель перед прунингом.
        
        Args:
            model: Модель для анализа
            
        Returns:
            Dict[str, Any]: Статистика модели
        """
        stats = {
            "total_params": 0,
            "zero_params": 0,
            "layers": {}
        }
        
        for name, module in model.named_modules():
            if isinstance(module, (torch.nn.Linear, torch.nn.Conv2d)):
                params = torch.numel(module.weight)
                zeros = torch.sum(module.weight == 0).item()
                stats["total_params"] += params
                stats["zero_params"] += zeros
                stats["layers"][name] = {
                    "type": module.__class__.__name__,
                    "params": params,
                    "zeros": zeros,
                    "sparsity": zeros / params if params > 0 else 0
                }
        
        return stats
    
    def prune_model(
        self,
        model: torch.nn.Module,
        layer_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Применяет прунинг к модели.
        
        Args:
            model: Модель для прунинга
            layer_types: Типы слоев для прунинга (по умолчанию Linear и Conv2d)
            
        Returns:
            Dict[str, Any]: Результаты прунинга
        """
        if layer_types is None:
            layer_types = ["Linear", "Conv2d"]
            
        pruning_fn = self._get_pruning_method()
        before_stats = self.analyze_model(model)
        
        # Применяем прунинг
        for name, module in model.named_modules():
            if any(isinstance(module, getattr(torch.nn, t)) for t in layer_types):
                pruning_fn(module, name='weight', amount=self.amount)
                prune.remove(module, 'weight')  # Делаем прунинг постоянным
        
        after_stats = self.analyze_model(model)
        
        results = {
            "method": self.pruning_method,
            "amount": self.amount,
            "before": before_stats,
            "after": after_stats,
            "compression_ratio": before_stats["total_params"] / (after_stats["total_params"] - after_stats["zero_params"])
        }
        
        # Сохраняем результаты
        output_file = self.save_dir / f"pruning_results_{self.pruning_method}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=4)
        
        logger.info(f"Результаты прунинга сохранены в {output_file}")
        return results
    
    @staticmethod
    def print_summary(results: Dict[str, Any]) -> None:
        """
        Выводит сводку результатов прунинга.
        
        Args:
            results: Результаты прунинга
        """
        print("\n=== Результаты прунинга ===")
        print(f"Метод: {results['method']}")
        print(f"Доля параметров для удаления: {results['amount']:.2%}")
        print(f"\nДо прунинга:")
        print(f"Всего параметров: {results['before']['total_params']:,}")
        print(f"Нулевых параметров: {results['before']['zero_params']:,}")
        print(f"Начальная разреженность: {results['before']['zero_params']/results['before']['total_params']:.2%}")
        print(f"\nПосле прунинга:")
        print(f"Всего параметров: {results['after']['total_params']:,}")
        print(f"Нулевых параметров: {results['after']['zero_params']:,}")
        print(f"Конечная разреженность: {results['after']['zero_params']/results['after']['total_params']:.2%}")
        print(f"\nКоэффициент сжатия: {results['compression_ratio']:.2f}x") 