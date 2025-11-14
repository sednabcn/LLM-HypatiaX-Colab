"""
Unit tests for configuration system.
Tests paths, model configs, and constants.
"""

import pytest
from pathlib import Path
from hypatiax.config import (
    config,
    paths,
    PathConfig,
    ModelConfig,
    TrainingConfig,
    DataConfig,
    EntityLabels,
    FileFormats,
    DEFAULT_STOPWORDS
)


class TestPathConfig:
    """Tests for PathConfig class"""
    
    def test_path_config_initialization(self):
        """Test that PathConfig initializes correctly"""
        pc = PathConfig()
        
        assert pc.root.exists()
        assert pc.hypatiax.exists()
        assert isinstance(pc.environment, str)
    
    def test_core_paths_exist(self):
        """Test that core paths are set correctly"""
        assert paths.root is not None
        assert paths.hypatiax is not None
        assert paths.datasets is not None
        assert paths.outputs is not None
    
    def test_get_output_path(self):
        """Test output path creation"""
        output = paths.get_output_path('test', 'subdir', 'file.txt')
        
        assert isinstance(output, Path)
        assert 'outputs' in str(output)
        assert 'test' in str(output)
        assert 'subdir' in str(output)
    
    def test_get_dataset_path(self):
        """Test dataset path creation"""
        dataset_path = paths.get_dataset_path(
            domain='queries',
            sub_domain='tableau',
            action='training'
        )
        
        assert isinstance(dataset_path, Path)
        assert 'queries' in str(dataset_path)
        assert 'tableau' in str(dataset_path)
        assert 'training' in str(dataset_path)
    
    def test_get_model_path(self):
        """Test model path creation"""
        model_path = paths.get_model_path(
            domain='queries',
            sub_domain='tableau',
            model_name='ner_tableau_desc'
        )
        
        assert isinstance(model_path, Path)
        assert 'data_spacy' in str(model_path)
        assert 'ner_tableau_desc' in str(model_path)
    
    def test_validate_path_exists(self):
        """Test path validation for existing path"""
        is_valid = paths.validate_path(paths.root)
        assert is_valid is True
    
    def test_validate_path_nonexistent(self):
        """Test path validation for non-existent path"""
        is_valid = paths.validate_path('/nonexistent/path/12345')
        assert is_valid is False
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        path_dict = paths.to_dict()
        
        assert isinstance(path_dict, dict)
        assert 'environment' in path_dict
        assert 'root' in path_dict
        assert 'datasets' in path_dict


class TestTrainingConfig:
    """Tests for TrainingConfig class"""
    
    def test_default_initialization(self):
        """Test default training config"""
        config = TrainingConfig()
        
        assert config.niter == 100
        assert config.batchsize == 8
        assert config.drop == 0.5
        assert config.patience == 5
        assert isinstance(config.output_model_name, str)
    
    def test_custom_initialization(self):
        """Test custom training config"""
        config = TrainingConfig(
            niter=50,
            batchsize=16,
            patience=10
        )
        
        assert config.niter == 50
        assert config.batchsize == 16
        assert config.patience == 10
    
    def test_to_dict(self):
        """Test conversion to dictionary"""
        config = TrainingConfig(niter=50)
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['niter'] == 50
        assert 'batchsize' in config_dict
    
    def test_update(self):
        """Test updating configuration"""
        config = TrainingConfig()
        original_niter = config.niter
        
        config.update(niter=200, batchsize=32)
        
        assert config.niter == 200
        assert config.niter != original_niter
        assert config.batchsize == 32
    
    def test_quick_train_preset(self):
        """Test quick training preset"""
        config = TrainingConfig.quick_train()
        
        assert config.niter == 10
        assert config.batchsize == 4
        assert config.patience == 3
    
    def test_production_preset(self):
        """Test production preset"""
        config = TrainingConfig.production()
        
        assert config.niter == 200
        assert config.batchsize == 16
        assert config.patience == 10


class TestDataConfig:
    """Tests for DataConfig class"""
    
    def test_default_initialization(self):
        """Test default data config"""
        config = DataConfig()
        
        assert config.modules == 'datasets'
        assert config.domain == 'queries'
        assert config.sub_domain == 'tableau'
        assert config.test_size == 0.2
    
    def test_for_descriptions_preset(self):
        """Test descriptions preset"""
        config = DataConfig.for_descriptions()
        
        assert config.dtype == 'desc'
        assert 'desc' in config.ner_entity
    
    def test_for_formulas_preset(self):
        """Test formulas preset"""
        config = DataConfig.for_formulas()
        
        assert config.dtype == 'formulas'
        assert 'formulas' in config.ner_entity
    
    def test_for_combined_preset(self):
        """Test combined preset"""
        config = DataConfig.for_combined()
        
        assert config.dtype == 'combined'
        assert 'combined' in config.ner_entity
    
    def test_update(self):
        """Test updating data config"""
        config = DataConfig()
        config.update(test_size=0.3, sizefile='lg')
        
        assert config.test_size == 0.3
        assert config.sizefile == 'lg'


class TestModelConfig:
    """Tests for ModelConfig class"""
    
    def test_training_desc(self):
        """Test description training config"""
        config = ModelConfig.training_desc(niter=100, batchsize=8)
        
        assert config.training.niter == 100
        assert config.training.batchsize == 8
        assert config.data.dtype == 'desc'
        assert 'desc' in config.training.output_model_name
    
    def test_training_formulas(self):
        """Test formulas training config"""
        config = ModelConfig.training_formulas(niter=150)
        
        assert config.training.niter == 150
        assert config.data.dtype == 'formulas'
        assert 'formulas' in config.training.output_model_name
    
    def test_training_combined(self):
        """Test combined training config"""
        config = ModelConfig.training_combined()
        
        assert config.data.dtype == 'combined'
        assert 'combined' in config.training.output_model_name
    
    def test_quick_test(self):
        """Test quick test config"""
        config = ModelConfig.quick_test()
        
        assert config.training.niter == 10  # Quick train preset
        assert config.data.dtype == 'desc'
    
    def test_to_dict(self):
        """Test model config to dict"""
        config = ModelConfig.training_desc()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'training' in config_dict
        assert 'data' in config_dict
        assert isinstance(config_dict['training'], dict)
        assert isinstance(config_dict['data'], dict)


class TestEntityLabels:
    """Tests for EntityLabels class"""
    
    def test_tableau_desc_labels(self):
        """Test description labels"""
        labels = EntityLabels.TABLEAU_DESC
        
        assert isinstance(labels, list)
        assert 'FUNCTION' in labels
        assert 'FIELD' in labels
        assert len(labels) > 0
    
    def test_tableau_formulas_labels(self):
        """Test formula labels"""
        labels = EntityLabels.TABLEAU_FORMULAS
        
        assert isinstance(labels, list)
        assert 'FUNCTION' in labels
        assert 'BRACKET' in labels
    
    def test_get_all_labels(self):
        """Test getting all unique labels"""
        all_labels = EntityLabels.get_all_labels()
        
        assert isinstance(all_labels, set)
        assert len(all_labels) > 0
    
    def test_get_labels_for_desc(self):
        """Test getting labels for descriptions"""
        labels = EntityLabels.get_labels_for('desc')
        
        assert labels == EntityLabels.TABLEAU_DESC
    
    def test_get_labels_for_formulas(self):
        """Test getting labels for formulas"""
        labels = EntityLabels.get_labels_for('formulas')
        
        assert labels == EntityLabels.TABLEAU_FORMULAS
    
    def test_get_labels_for_combined(self):
        """Test getting labels for combined"""
        labels = EntityLabels.get_labels_for('combined')
        
        assert labels == EntityLabels.TABLEAU_COMBINED
    
    def test_get_labels_for_invalid(self):
        """Test getting labels with invalid type"""
        with pytest.raises(ValueError):
            EntityLabels.get_labels_for('invalid_type')


class TestFileFormats:
    """Tests for FileFormats class"""
    
    def test_is_supported_excel(self):
        """Test Excel file support"""
        assert FileFormats.is_supported('data.xlsx') is True
        assert FileFormats.is_supported('data.xls') is True
    
    def test_is_supported_csv(self):
        """Test CSV file support"""
        assert FileFormats.is_supported('data.csv') is True
    
    def test_is_supported_json(self):
        """Test JSON file support"""
        assert FileFormats.is_supported('data.json') is True
        assert FileFormats.is_supported('data.jsonl') is True
    
    def test_is_supported_spacy(self):
        """Test spaCy file support"""
        assert FileFormats.is_supported('data.spacy') is True
    
    def test_is_supported_unsupported(self):
        """Test unsupported file format"""
        assert FileFormats.is_supported('data.pdf') is False
        assert FileFormats.is_supported('data.docx') is False
    
    def test_get_type_excel(self):
        """Test getting Excel file type"""
        assert FileFormats.get_type('data.xlsx') == 'excel'
        assert FileFormats.get_type('data.xls') == 'excel'
    
    def test_get_type_csv(self):
        """Test getting CSV file type"""
        assert FileFormats.get_type('data.csv') == 'csv'
    
    def test_get_type_json(self):
        """Test getting JSON file type"""
        assert FileFormats.get_type('data.json') == 'json'
        assert FileFormats.get_type('data.jsonl') == 'jsonl'
    
    def test_get_type_unknown(self):
        """Test getting unknown file type"""
        assert FileFormats.get_type('data.unknown') == 'unknown'


class TestMainConfig:
    """Tests for main Config class"""
    
    def test_config_initialization(self):
        """Test main config initialization"""
        assert config.paths is not None
        assert config.models is not None
        assert config.entities is not None
        assert isinstance(config.environment, str)
    
    def test_config_environment_detection(self):
        """Test environment detection"""
        env = config.environment
        
        assert env in ['local', 'colab', 'github', 'kaggle', 'docker']
    
    def test_config_debug_mode(self):
        """Test debug mode"""
        assert isinstance(config.debug_mode, bool)
    
    def test_config_get(self):
        """Test getting config values"""
        root = config.get('paths.root')
        assert root is not None


class TestConstants:
    """Tests for constants"""
    
    def test_default_stopwords(self):
        """Test default stopwords"""
        assert isinstance(DEFAULT_STOPWORDS, list)
        assert len(DEFAULT_STOPWORDS) > 0
        assert 'the' in DEFAULT_STOPWORDS
        assert 'and' in DEFAULT_STOPWORDS
    
    def test_stopwords_lowercase(self):
        """Test that stopwords are lowercase"""
        for word in DEFAULT_STOPWORDS:
            assert word.islower() or not word.isalpha()


# Integration tests
class TestConfigIntegration:
    """Integration tests for config system"""
    
    def test_full_workflow_desc(self):
        """Test complete workflow for description training"""
        # Get config
        model_config = ModelConfig.training_desc(niter=10, batchsize=4)
        
        # Get paths
        data_path = paths.get_dataset_path(
            action='training',
            filename=model_config.data.filename
        )
        
        output_path = paths.get_output_path(
            'models',
            model_config.training.output_model_name
        )
        
        # Get labels
        labels = EntityLabels.get_labels_for(model_config.data.dtype)
        
        # Verify everything works together
        assert data_path is not None
        assert output_path is not None
        assert len(labels) > 0
        assert model_config.training.niter == 10
    
    def test_config_to_dict_complete(self):
        """Test converting complete config to dict"""
        model_config = ModelConfig.training_desc()
        config_dict = model_config.to_dict()
        
        # Verify structure
        assert 'training' in config_dict
        assert 'data' in config_dict
        
        # Verify training params
        assert 'niter' in config_dict['training']
        assert 'batchsize' in config_dict['training']
        
        # Verify data params
        assert 'filename' in config_dict['data']
        assert 'dtype' in config_dict['data']
