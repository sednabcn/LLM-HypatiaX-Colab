"""
Model and Training Configuration

Centralized configurations for model training, data processing, and evaluation.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TrainingConfig:
    """
    Configuration for model training.

    Usage:
        config = TrainingConfig(niter=50, batchsize=16)
        config_dict = config.to_dict()
    """

    # Training parameters
    niter: int = 100  # Number of iterations
    batchsize: int = 8  # Batch size
    drop: float = 0.5  # Dropout rate
    patience: int = 5  # Early stopping patience
    n_checkpoint: int = 10  # Checkpoint frequency

    # Learning parameters
    learn_rate: float = 0.001  # Initial learning rate

    # Model parameters
    output_model_name: str = "ner_model"  # Output model name

    # Validation
    use_validation: bool = True  # Use validation set
    val_split: float = 0.1  # Validation split ratio

    # Logging
    verbose: bool = True  # Print training progress
    log_frequency: int = 10  # Log every N iterations

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def update(self, **kwargs) -> "TrainingConfig":
        """Update configuration with new values"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    @classmethod
    def quick_train(cls) -> "TrainingConfig":
        """Quick training config (for testing)"""
        return cls(niter=10, batchsize=4, patience=3, n_checkpoint=5)

    @classmethod
    def production(cls) -> "TrainingConfig":
        """Production training config (best quality)"""
        return cls(niter=200, batchsize=16, patience=10, n_checkpoint=20, drop=0.3)


@dataclass
class DataConfig:
    """
    Configuration for data processing.

    Usage:
        config = DataConfig.for_descriptions()
        config.update(test_size=0.3)
    """

    # Data source
    modules: str = "datasets"
    domain: str = "queries"
    sub_domain: str = "tableau"
    actions: str = "training"

    # File info
    filename: str = "formulas_nor.xlsx"
    dtype: str = "desc"  # 'desc', 'formulas', or 'combined'
    sizefile: str = "sm"  # 'sm', 'md', 'lg'

    # Processing
    test_size: float = 0.2
    val_data: bool = True
    task_type: str = "single"  # 'single' or 'multi'
    option: Optional[str] = None

    # NER entity name
    ner_entity: str = "ner_tableau_desc"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    def update(self, **kwargs) -> "DataConfig":
        """Update configuration"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self

    @classmethod
    def for_descriptions(cls) -> "DataConfig":
        """Config for description data"""
        return cls(filename="formulas_nor.xlsx", dtype="desc", ner_entity="ner_tableau_desc")

    @classmethod
    def for_formulas(cls) -> "DataConfig":
        """Config for formula data"""
        return cls(filename="formulas_nor.xlsx", dtype="formulas", ner_entity="ner_tableau_formulas")

    @classmethod
    def for_combined(cls) -> "DataConfig":
        """Config for combined data"""
        return cls(filename="formulas_nor.xlsx", dtype="combined", ner_entity="ner_tableau_combined")


@dataclass
class ModelConfig:
    """
    Complete model configuration combining training and data configs.

    Usage:
        config = ModelConfig.training_desc()
        print(config.training.niter)
        print(config.data.filename)
    """

    training: TrainingConfig = field(default_factory=TrainingConfig)
    data: DataConfig = field(default_factory=DataConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entire config to dictionary"""
        return {"training": self.training.to_dict(), "data": self.data.to_dict()}

    @classmethod
    def training_desc(cls, niter: int = 100, batchsize: int = 8, sizefile: str = "sm") -> "ModelConfig":
        """
        Config for training description NER model.

        Args:
            niter: Number of training iterations
            batchsize: Batch size
            sizefile: Dataset size ('sm', 'md', 'lg')

        Returns:
            Complete model configuration
        """
        return cls(
            training=TrainingConfig(niter=niter, batchsize=batchsize, output_model_name="ner_tableau_desc"),
            data=DataConfig.for_descriptions().update(sizefile=sizefile),
        )

    @classmethod
    def training_formulas(cls, niter: int = 100, batchsize: int = 8, sizefile: str = "sm") -> "ModelConfig":
        """Config for training formula NER model"""
        return cls(
            training=TrainingConfig(niter=niter, batchsize=batchsize, output_model_name="ner_tableau_formulas"),
            data=DataConfig.for_formulas().update(sizefile=sizefile),
        )

    @classmethod
    def training_combined(cls, niter: int = 150, batchsize: int = 8, sizefile: str = "md") -> "ModelConfig":
        """Config for training combined model"""
        return cls(
            training=TrainingConfig(niter=niter, batchsize=batchsize, output_model_name="ner_tableau_combined"),
            data=DataConfig.for_combined().update(sizefile=sizefile),
        )

    @classmethod
    def quick_test(cls) -> "ModelConfig":
        """Quick config for testing (fast training)"""
        return cls(training=TrainingConfig.quick_train(), data=DataConfig.for_descriptions())


@dataclass
class EvaluationConfig:
    """Configuration for model evaluation"""

    batch_size: int = 27
    metrics: List[str] = field(default_factory=lambda: ["ents_f", "ents_p", "ents_r", "ents_per_type"])
    save_results: bool = True
    output_format: str = "json"  # 'json', 'csv', 'txt'

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Convenience functions for quick access
def get_training_config(model_type: str = "desc", **kwargs) -> ModelConfig:
    """
    Quick access to training configurations.

    Args:
        model_type: 'desc', 'formulas', or 'combined'
        **kwargs: Override default parameters

    Returns:
        ModelConfig instance

    Example:
        config = get_training_config('desc', niter=50, batchsize=16)
    """
    if model_type == "desc":
        config = ModelConfig.training_desc()
    elif model_type == "formulas":
        config = ModelConfig.training_formulas()
    elif model_type == "combined":
        config = ModelConfig.training_combined()
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    # Update with kwargs
    if kwargs:
        for key, value in kwargs.items():
            if hasattr(config.training, key):
                setattr(config.training, key, value)
            elif hasattr(config.data, key):
                setattr(config.data, key, value)

    return config
