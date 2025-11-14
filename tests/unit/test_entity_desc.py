"""
Test entity description with proper path management.
Works from any location - no hardcoded paths!
"""
import spacy
import pandas as pd
from importlib import resources

from hypatiax.custom_ner.queries.tableau import (
    custom_tableau_desc_components,
    custom_tableau_formulas_components, 
    custom_tableau_components
)
from hypatiax.custom_entities.ner_entity import Custom_ner_entities
from hypatiax.utils.utils import save_spacy_training_data, save_spacy_training_data_to_json
from hypatiax.utils.files import FilesManager

# Import path configuration
try:
    from hypatiax.config import config
except ImportError:
    # Fallback: use basic PathConfig
    from pathlib import Path
    import os
    
    class SimpleConfig:
        def __init__(self):
            self.root = Path.cwd()
            self.outputs = self.root / 'outputs'
            self.outputs.mkdir(exist_ok=True)
        
        def get_output_path(self, *parts):
            path = self.outputs.joinpath(*parts)
            path.parent.mkdir(parents=True, exist_ok=True)
            return path
    
    config = SimpleConfig()


# ============================================================================
# CONFIGURATION
# ============================================================================

SAVE_OPTION = 0  # 0 = no save, 1 = save
NAME_COL = 'Description'

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Run entity description test."""
    
    print("=" * 70)
    print("Entity Description Test - HypatiaX")
    print("=" * 70)
    
    # Show configuration
    if hasattr(config, 'print_paths'):
        config.print_paths()
    else:
        print(f"\nOutput Directory: {config.outputs}\n")
    
    # ========================================================================
    # LOAD DATA
    # ========================================================================
    
    print("\n📂 Loading data...")
    
    # Load training data
    F = FilesManager('datasets', 'queries', 'tableau', 'training')
    data = F.load('formulas_nor.xlsx')
    print(f"   ✅ Training data loaded: {len(data)} rows")
    
    # Load testing data
    G = FilesManager('datasets', 'queries', 'tableau', 'testing')
    data_t = G.load('formulas_test_nor.xlsx')
    print(f"   ✅ Testing data loaded: {len(data_t)} rows")
    
    # Get NER model path using resources (works with installed packages)
    path_ner = resources.files('hypatiax.data_spacy.queries.tableau') / 'ner_tableau_desc'
    print(f"   ✅ NER path: {path_ner}")
    
    # ========================================================================
    # TRAIN
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("TRAINING DATA PROCESSING")
    print("=" * 70)
    
    ent_desc, Train_desc_data = Custom_ner_entities(
        data, 
        path_ner, 
        NAME_COL
    ).get_entity()
    
    print(f"\n📊 Training Entities: {ent_desc}")
    print(f"📊 Training Samples: {len(Train_desc_data)}")
    
    if Train_desc_data:
        print("\nSample Training Data:")
        for i, item in enumerate(Train_desc_data[:3]):  # Show first 3
            print(f"  {i+1}. {item}")
        if len(Train_desc_data) > 3:
            print(f"  ... and {len(Train_desc_data) - 3} more")
    
    # ========================================================================
    # TEST
    # ========================================================================
    
    print("\n" + "=" * 70)
    print("TESTING DATA PROCESSING")
    print("=" * 70)
    
    ent_test_desc, Test_desc_data = Custom_ner_entities(
        data_t, 
        path_ner, 
        NAME_COL
    ).get_entity()
    
    print(f"\n📊 Testing Entities: {ent_test_desc}")
    print(f"📊 Testing Samples: {len(Test_desc_data)}")
    
    if Test_desc_data:
        print("\nSample Testing Data:")
        for i, item in enumerate(Test_desc_data[:3]):  # Show first 3
            print(f"  {i+1}. {item}")
        if len(Test_desc_data) > 3:
            print(f"  ... and {len(Test_desc_data) - 3} more")
    
    # ========================================================================
    # SAVE (if enabled)
    # ========================================================================
    
    if SAVE_OPTION != 0:
        print("\n" + "=" * 70)
        print("SAVING DATA")
        print("=" * 70)
        
        # Define output paths using config
        path_tr = config.get_output_path('spacy_data', 'training_spacy')
        path_te = config.get_output_path('spacy_data', 'testing_spacy')
        path_vo = config.get_output_path('spacy_data', 'vocab')
        
        # Alternative save location in datasets
        path_tr_datasets = config.get_output_path('datasets', 'tableau', 'training_spacy')
        path_te_datasets = config.get_output_path('datasets', 'tableau', 'testing_spacy')
        
        print(f"\n💾 Saving to:")
        print(f"   Training: {path_tr}")
        print(f"   Testing:  {path_te}")
        print(f"   Vocab:    {path_vo}")
        
        try:
            # Save training data
            print("\n📝 Saving training data...")
            save_spacy_training_data(
                str(path_tr),
                Train_desc_data,
                "Train_tableau_desc_sm_data",
                path_ner
            )
            save_spacy_training_data_to_json(
                str(path_tr_datasets),
                Train_desc_data,
                "Train_tableau_desc_sm_data"
            )
            print("   ✅ Training data saved")
            
            # Save test data
            print("\n📝 Saving test data...")
            save_spacy_training_data(
                str(path_te),
                Test_desc_data,
                "Test_tableau_desc_sm_data",
                path_ner
            )
            save_spacy_training_data_to_json(
                str(path_te_datasets),
                Test_desc_data,
                "Test_tableau_desc_sm_data"
            )
            print("   ✅ Test data saved")
            
            # Save vocabulary
            print("\n📝 Saving vocabulary...")
            save_spacy_training_data_to_json(
                str(path_vo),
                ent_desc,
                "vocab_tableau_desc_Description_sm"
            )
            print("   ✅ Vocabulary saved")
            
            print(f"\n✅ All data saved successfully!")
            
        except Exception as e:
            print(f"\n❌ Error saving data: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("\n" + "=" * 70)
        print("ℹ️  Saving disabled (SAVE_OPTION = 0)")
        print("   Set SAVE_OPTION = 1 to save processed data")
        print("=" * 70)
    
    print("\n✅ Test completed successfully!")


if __name__ == "__main__":
    main()
