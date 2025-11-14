# tests/integration/test_[workflow_name].py
"""
Integration tests for [workflow_name].
Tests end-to-end workflows with real data and file I/O.
"""

import pytest
from pathlib import Path
from hypatiax.[module] import load_data, process_data, save_results


class TestEndToEndWorkflow:
    """Tests for complete workflow"""
    
    def test_full_pipeline(self, temp_output_dir):
        """Test entire pipeline from load to save"""
        # Arrange
        input_file = "datasets/test_data.xlsx"
        output_file = temp_output_dir / "results.json"
        
        # Act
        data = load_data(input_file)
        processed = process_data(data)
        save_results(processed, output_file)
        
        # Assert
        assert output_file.exists()
        assert processed is not None
        assert len(processed) > 0
    
    def test_with_real_config(self, base_config, temp_model_dir):
        """Test with real configuration"""
        config = base_config
        config['output_dir'] = str(temp_model_dir)
        
        # Run workflow
        result = run_training_pipeline(config)
        
        # Verify outputs
        assert result['success'] is True
        assert (temp_model_dir / "model").exists()
    
    def test_multiple_components_interact(self):
        """Test that multiple components work together"""
        # Component A
        data_a = load_descriptions()
        
        # Component B  
        data_b = load_formulas()
        
        # Integration
        merged = merge_components(data_a, data_b)
        
        assert merged is not None
        assert 'Description' in merged.columns
        assert 'Formulas' in merged.columns


@pytest.mark.slow
def test_long_running_workflow(training_config):
    """Test that takes longer to run"""
    model = train_model(training_config)
    assert model is not None
