import pandas as pd
import logging
import os
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

"""
NER Model Testing Simulation Packages
Provides three different simulation modes for testing NER training pipelines:
1. Quick simulation - Fast mock results for testing infrastructure
2. Realistic simulation - Mimics actual training behavior with delays
3. Full integration - Actual function calls (requires hypatiax package)
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ============================================================================
# TEST CONFIGURATIONS
# ============================================================================

def get_test_configurations() -> List[Dict]:
    """
    Get standard test configurations for NER training.
    
    Returns:
        List of test configuration dictionaries
    """
    return [
        {
            'test_id': '1',
            'name': 'Description_Small',
            'data_prep': {
                'modules': 'datasets',
                'domain': 'queries',
                'sub_domain': 'tableau',
                'actions': 'training',
                'filename': 'formulas_nor.xlsx',
                'dtype': 'desc',
                'sizefile': 'sm',
                'test_size': 0.2,
                'task_type': 'single',
                'ner_entity': 'ner_tableau_desc',
                'dataset_normalized': None,
                'val_data': True,
                'option': None
            },
            'training': {
                'domain': 'queries',
                'sub_domain': 'tableau',
                'dtype': 'desc',
                'output_model_name': 'Description_sm',
                'niter': 400,
                'drop': 0.5,
                'batchsize': 8,
                'patience': 10,
                'n_checkpoint': 100,
                'option': None
            }
        },
        {
            'test_id': '2',
            'name': 'Formulas_Small',
            'data_prep': {
                'modules': 'datasets',
                'domain': 'queries',
                'sub_domain': 'tableau',
                'actions': 'training',
                'filename': 'formulas_nor.xlsx',
                'dtype': 'formulas',
                'sizefile': 'sm',
                'test_size': 0.2,
                'task_type': 'single',
                'ner_entity': 'ner_tableau_formulas',
                'dataset_normalized': None,
                'val_data': True,
                'option': None
            },
            'training': {
                'domain': 'queries',
                'sub_domain': 'tableau',
                'dtype': 'formulas',
                'output_model_name': 'Formulas_sm',
                'niter': 400,
                'drop': 0.5,
                'batchsize': 8,
                'patience': 10,
                'n_checkpoint': 100,
                'option': None
            }
        },
        {
            'test_id': '3',
            'name': 'Combined_Large',
            'data_prep': {
                'modules': 'datasets',
                'domain': 'queries',
                'sub_domain': 'tableau',
                'actions': 'training',
                'filename': 'formulas_nor_combined.xlsx',
                'dtype': 'both',
                'sizefile': 'bsm',
                'test_size': 0.2,
                'task_type': 'single',
                'ner_entity': 'ner_tableau',
                'dataset_normalized': None,
                'val_data': True,
                'option': 'split'
            },
            'training': {
                'domain': 'queries',
                'sub_domain': 'tableau',
                'dtype': 'both',
                'output_model_name': 'Combined_bsm',
                'niter': 400,
                'drop': 0.5,
                'batchsize': 8,
                'patience': 10,
                'n_checkpoint': 100,
                'option': None
            }
        }
    ]


# ============================================================================
# SIMULATION MODE 1: QUICK MOCK
# ============================================================================

def simulate_quick_test(config: Dict) -> Dict:
    """
    Quick simulation with instant results for infrastructure testing.
    
    Args:
        config: Test configuration dictionary
        
    Returns:
        Simulated test results
    """
    test_id = config['test_id']
    logging.info(f"Quick simulation - Test {test_id}: {config['name']}")
    
    # Simulate different data sizes
    size_map = {'sm': 100, 'bsm': 500, 'bg': 1000}
    sizefile = config['data_prep']['sizefile']
    base_samples = size_map.get(sizefile, 100)
    
    # Mock data preparation
    train_samples = int(base_samples * 0.6)
    val_samples = int(base_samples * 0.2)
    test_samples = int(base_samples * 0.2)
    
    # Mock performance metrics (with some variation)
    base_f1 = random.uniform(0.75, 0.92)
    
    result = {
        'test_id': test_id,
        'name': config['name'],
        'status': 'completed',
        'dtype': config['data_prep']['dtype'],
        'sizefile': sizefile,
        'model_name': config['training']['output_model_name'],
        'train_samples': train_samples,
        'val_samples': val_samples,
        'test_samples': test_samples,
        'val_precision': round(base_f1 + random.uniform(-0.03, 0.03), 4),
        'val_recall': round(base_f1 + random.uniform(-0.03, 0.03), 4),
        'val_f1': round(base_f1, 4),
        'test_precision': round(base_f1 + random.uniform(-0.05, 0.02), 4),
        'test_recall': round(base_f1 + random.uniform(-0.05, 0.02), 4),
        'test_f1': round(base_f1 + random.uniform(-0.04, 0.01), 4),
        'training_time': round(random.uniform(30, 120), 2)
    }
    
    logging.info(f"Test {test_id} - Simulated F1: {result['test_f1']:.4f}")
    return result


# ============================================================================
# SIMULATION MODE 2: REALISTIC SIMULATION
# ============================================================================

def simulate_realistic_test(config: Dict) -> Dict:
    """
    Realistic simulation that mimics actual training behavior with delays.
    
    Args:
        config: Test configuration dictionary
        
    Returns:
        Simulated test results with realistic timing
    """
    test_id = config['test_id']
    test_name = config['name']
    
    logging.info(f"Realistic simulation - Test {test_id}: {test_name}")
    
    result = {
        'test_id': test_id,
        'name': test_name,
        'status': 'failed',
        'dtype': config['data_prep']['dtype'],
        'sizefile': config['data_prep']['sizefile'],
        'model_name': config['training']['output_model_name']
    }
    
    try:
        # Step 1: Simulate data preparation (1-3 seconds)
        logging.info(f"Test {test_id} - [1/4] Preparing data...")
        time.sleep(random.uniform(1, 3))
        
        size_map = {'sm': 100, 'bsm': 500, 'bg': 1000}
        base_samples = size_map.get(config['data_prep']['sizefile'], 100)
        
        train_samples = int(base_samples * 0.6)
        val_samples = int(base_samples * 0.2)
        test_samples = int(base_samples * 0.2)
        
        result.update({
            'train_samples': train_samples,
            'val_samples': val_samples,
            'test_samples': test_samples
        })
        
        logging.info(f"Test {test_id} - Train: {train_samples}, Val: {val_samples}, Test: {test_samples}")
        
        # Step 2: Simulate training (5-15 seconds based on size)
        logging.info(f"Test {test_id} - [2/4] Training model...")
        niter = config['training']['niter']
        training_time = (niter / 100) * random.uniform(1.5, 3.0)
        time.sleep(min(training_time / 50, 5))  # Scaled down for demo
        
        result['training_time'] = round(training_time, 2)
        logging.info(f"Test {test_id} - Estimated training time: {training_time:.2f}s")
        
        # Step 3: Simulate validation (1-2 seconds)
        logging.info(f"Test {test_id} - [3/4] Validating model...")
        time.sleep(random.uniform(0.5, 1))
        
        # Generate realistic metrics based on config
        dtype = config['data_prep']['dtype']
        base_f1_map = {'desc': 0.85, 'formulas': 0.82, 'both': 0.88}
        base_f1 = base_f1_map.get(dtype, 0.85)
        
        # Add some noise
        val_f1 = base_f1 + random.uniform(-0.05, 0.08)
        val_precision = val_f1 + random.uniform(-0.03, 0.04)
        val_recall = val_f1 + random.uniform(-0.04, 0.03)
        
        result.update({
            'val_precision': round(max(0, min(1, val_precision)), 4),
            'val_recall': round(max(0, min(1, val_recall)), 4),
            'val_f1': round(max(0, min(1, val_f1)), 4)
        })
        
        logging.info(f"Test {test_id} - Validation F1: {result['val_f1']:.4f}")
        
        # Step 4: Simulate testing (1-2 seconds)
        logging.info(f"Test {test_id} - [4/4] Testing model...")
        time.sleep(random.uniform(0.5, 1))
        
        # Test metrics usually slightly lower than validation
        test_f1 = val_f1 - random.uniform(0.01, 0.04)
        test_precision = test_f1 + random.uniform(-0.02, 0.03)
        test_recall = test_f1 + random.uniform(-0.03, 0.02)
        
        result.update({
            'test_precision': round(max(0, min(1, test_precision)), 4),
            'test_recall': round(max(0, min(1, test_recall)), 4),
            'test_f1': round(max(0, min(1, test_f1)), 4)
        })
        
        result['status'] = 'completed'
        logging.info(f"Test {test_id} - Test F1: {result['test_f1']:.4f} - COMPLETED")
        
    except Exception as e:
        logging.error(f"Test {test_id} - Error: {e}")
        result['error'] = str(e)
    
    return result


# ============================================================================
# SIMULATION MODE 3: FULL INTEGRATION (requires hypatiax)
# ============================================================================

def run_full_integration_test(config: Dict) -> Dict:
    """
    Full integration test with actual hypatiax function calls.
    
    Args:
        config: Test configuration dictionary
        
    Returns:
        Actual test results
    """
    try:
        from hypatiax.core.preprocessing.preparation_data import preparation_data
        from hypatiax.core.training.training_spacy import Training
        from hypatiax.core.deployment.evaluation_model import evaluate_spacy_model
        from hypatiax.core.evaluation.testing_model import test_spacy_model
    except ImportError as e:
        logging.error(f"Cannot import hypatiax modules: {e}")
        return {
            'test_id': config['test_id'],
            'status': 'error',
            'error': 'hypatiax package not available'
        }
    
    test_id = config['test_id']
    test_name = config['name']
    
    logging.info(f"Full integration - Test {test_id}: {test_name}")
    
    result = {
        'test_id': test_id,
        'name': test_name,
        'status': 'failed',
        'dtype': config['data_prep']['dtype'],
        'sizefile': config['data_prep']['sizefile'],
        'model_name': config['training']['output_model_name']
    }
    
    try:
        # Step 1: Prepare data
        logging.info(f"Test {test_id} - [1/4] Preparing data...")
        X_train, X_val, X_test = preparation_data(**config['data_prep'])
        
        result.update({
            'train_samples': len(X_train) if X_train else 0,
            'val_samples': len(X_val) if X_val else 0,
            'test_samples': len(X_test) if X_test else 0
        })
        
        # Step 2: Train model
        logging.info(f"Test {test_id} - [2/4] Training model...")
        training_config = config['training'].copy()
        training_config['train_data'] = X_train
        training_config['val_data'] = X_val
        
        start_time = time.time()
        trainer = Training(**training_config)
        history, nlp = trainer.train()
        training_time = time.time() - start_time
        
        result['training_time'] = round(training_time, 2)
        
        # Step 3: Validate
        if X_val and len(X_val) > 0:
            logging.info(f"Test {test_id} - [3/4] Validating model...")
            val_scores = evaluate_spacy_model(nlp, X_val)
            result.update({
                'val_precision': round(val_scores.get('ents_p', 0.0), 4),
                'val_recall': round(val_scores.get('ents_r', 0.0), 4),
                'val_f1': round(val_scores.get('ents_f', 0.0), 4)
            })
        
        # Step 4: Test
        if X_test and len(X_test) > 0:
            logging.info(f"Test {test_id} - [4/4] Testing model...")
            test_scores = test_spacy_model(nlp, X_test)
            result.update({
                'test_precision': round(test_scores.get('ents_p', 0.0), 4),
                'test_recall': round(test_scores.get('ents_r', 0.0), 4),
                'test_f1': round(test_scores.get('ents_f', 0.0), 4)
            })
        
        result['status'] = 'completed'
        logging.info(f"Test {test_id} - COMPLETED")
        
    except Exception as e:
        logging.error(f"Test {test_id} - Error: {e}", exc_info=True)
        result['error'] = str(e)
    
    return result


# ============================================================================
# PARALLEL EXECUTION FRAMEWORK
# ============================================================================

def run_tests_parallel(mode: str = 'realistic', max_workers: Optional[int] = None) -> pd.DataFrame:
    """
    Run all tests in parallel using the specified simulation mode.
    
    Args:
        mode: Simulation mode - 'quick', 'realistic', or 'full'
        max_workers: Maximum number of parallel workers
        
    Returns:
        DataFrame with test results
    """
    # Select test function based on mode
    mode_map = {
        'quick': simulate_quick_test,
        'realistic': simulate_realistic_test,
        'full': run_full_integration_test
    }
    
    test_function = mode_map.get(mode.lower())
    if not test_function:
        raise ValueError(f"Invalid mode: {mode}. Choose from: {list(mode_map.keys())}")
    
    # Get configurations
    test_configs = get_test_configurations()
    
    if max_workers is None:
        max_workers = min(3, os.cpu_count() or 1)
    
    logging.info(f"="*70)
    logging.info(f"Starting parallel test execution")
    logging.info(f"Mode: {mode.upper()}")
    logging.info(f"Tests: {len(test_configs)}")
    logging.info(f"Workers: {max_workers}")
    logging.info(f"="*70)
    
    # Run tests in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_config = {
            executor.submit(test_function, config): config 
            for config in test_configs
        }
        
        for future in as_completed(future_to_config):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                config = future_to_config[future]
                logging.error(f"Unexpected error for test {config['test_id']}: {e}")
                results.append({
                    'test_id': config['test_id'],
                    'name': config.get('name', 'Unknown'),
                    'status': 'error',
                    'error': str(e)
                })
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort by test_id
    if 'test_id' in results_df.columns:
        results_df = results_df.sort_values('test_id')
    
    logging.info(f"="*70)
    logging.info("All tests completed")
    logging.info(f"="*70)
    
    return results_df


def print_results_summary(results_df: pd.DataFrame):
    """
    Print a formatted summary of test results.
    
    Args:
        results_df: DataFrame containing test results
    """
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    # Display main results
    display_cols = ['test_id', 'name', 'status', 'dtype', 'val_f1', 'test_f1', 'training_time']
    available_cols = [col for col in display_cols if col in results_df.columns]
    
    if available_cols:
        print(results_df[available_cols].to_string(index=False))
    
    # Statistics
    print("\n" + "-"*70)
    success_count = (results_df['status'] == 'completed').sum()
    error_count = (results_df['status'].isin(['failed', 'error'])).sum()
    
    print(f"Total Tests:    {len(results_df)}")
    print(f"Completed:      {success_count}")
    print(f"Failed/Errors:  {error_count}")
    
    # Best model
    if 'test_f1' in results_df.columns:
        completed = results_df[results_df['status'] == 'completed']
        if not completed.empty and completed['test_f1'].notna().any():
            best_idx = completed['test_f1'].idxmax()
            best = completed.loc[best_idx]
            print("\n" + "-"*70)
            print("BEST PERFORMING MODEL")
            print("-"*70)
            print(f"Test ID:   {best['test_id']}")
            print(f"Name:      {best.get('name', 'N/A')}")
            print(f"Model:     {best.get('model_name', 'N/A')}")
            print(f"Test F1:   {best['test_f1']:.4f}")
    
    print("="*70)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """
    Main execution function with mode selection.
    """
    import sys
    
    # Parse command line argument or default to realistic
    mode = sys.argv[1] if len(sys.argv) > 1 else 'realistic'
    
    print(f"\nRunning in {mode.upper()} mode...\n")
    
    # Run tests
    start_time = time.time()
    results_df = run_tests_parallel(mode=mode, max_workers=3)
    total_time = time.time() - start_time
    
    # Print results
    print_results_summary(results_df)
    
    print(f"\nTotal execution time: {total_time:.2f}s")
    
    # Save results
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f'test_results_{mode}_{timestamp}.csv'
    results_df.to_csv(filename, index=False)
    print(f"\n✓ Results saved to: {filename}")
    
    return results_df


if __name__ == "__main__":
    results = main()
