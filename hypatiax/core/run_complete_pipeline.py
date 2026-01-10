#!/usr/bin/python3
"""
MASTER INTEGRATION SCRIPT
Executes complete pipeline from data preparation to deployment
All steps: Preprocessing → Training → Evaluation → Deployment
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class PipelineConfig:
    """Configuration for complete pipeline"""

    def __init__(self):
        # Paths
        self.base_dir = Path(".")
        self.data_dir = self.base_dir / "data"
        self.preprocessed_dir = self.base_dir / "preprocessed_data"
        self.models_dir = self.base_dir / "models"
        self.results_dir = self.base_dir / "results"
        self.logs_dir = self.base_dir / "logs"

        # Data files
        self.raw_data_file = self.data_dir / "training_data.json"

        # Model configurations
        self.spacy_config = {"n_iter": 30, "batch_size": 8}

        self.transformer_config = {
            "model_name": "t5-small",
            "num_epochs": 5,
            "batch_size": 8,
        }

        self.rag_config = {"embedding_model": "all-MiniLM-L6-v2", "top_k": 5}

        # Pipeline steps
        self.steps = [
            "prepare_data",
            "train_spacy",
            "train_transformer",
            "train_rag",
            "train_llm",
            "evaluate_all",
            "deploy",
        ]


class PipelineExecutor:
    """Execute complete ML pipeline"""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self.results = {}
        self.start_time = None

        # Create directories
        self._create_directories()

        # Setup logging
        self._setup_logging()

    def _create_directories(self):
        """Create necessary directories"""
        for dir_path in [
            self.config.data_dir,
            self.config.preprocessed_dir,
            self.config.models_dir,
            self.config.results_dir,
            self.config.logs_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for different data formats
        (self.config.preprocessed_dir / "spacy").mkdir(exist_ok=True)
        (self.config.preprocessed_dir / "transformer").mkdir(exist_ok=True)
        (self.config.preprocessed_dir / "mapping").mkdir(exist_ok=True)
        (self.config.preprocessed_dir / "rag").mkdir(exist_ok=True)

    def _setup_logging(self):
        """Setup logging"""
        log_file = (
            self.config.logs_dir
            / f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        import logging

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def log(self, message: str, level: str = "info"):
        """Log message"""
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)

    def step_prepare_data(self):
        """Step 1: Data Preparation"""
        self.log("=" * 70)
        self.log("STEP 1: DATA PREPARATION")
        self.log("=" * 70)

        try:
            from preprocessing_pipeline import DataPreprocessor, PreprocessingConfig

            # Check if raw data exists
            if not self.config.raw_data_file.exists():
                self.log("Creating sample training data...", "warning")
                self._create_sample_data()

            # Initialize preprocessor
            prep_config = PreprocessingConfig(
                input_file=str(self.config.raw_data_file),
                output_dir=str(self.config.preprocessed_dir),
            )

            preprocessor = DataPreprocessor(prep_config)

            # Load and preprocess data
            self.log("Loading data...")
            data = preprocessor.load_data()
            self.log(f"Loaded {len(data)} examples")

            # Generate all formats
            self.log("Generating spaCy format...")
            preprocessor.prepare_spacy_format(data)

            self.log("Generating Transformer format...")
            preprocessor.prepare_transformer_format(data)

            self.log("Generating Mapping format...")
            preprocessor.prepare_mapping_format(data)

            self.log("Generating statistics...")
            stats = preprocessor.generate_statistics(data)

            self.log("✅ Data preparation complete")
            self.results["prepare_data"] = {
                "status": "success",
                "num_examples": len(data),
                "statistics": stats,
            }

            return True

        except Exception as e:
            self.log(f"❌ Data preparation failed: {e}", "error")
            self.results["prepare_data"] = {"status": "failed", "error": str(e)}
            return False

    def step_train_spacy(self):
        """Step 2: Train spaCy NER Model"""
        self.log("=" * 70)
        self.log("STEP 2: TRAIN SPACY NER MODEL")
        self.log("=" * 70)

        try:
            from training_spacy import train_spacy_ner

            train_file = self.config.preprocessed_dir / "spacy" / "train_spacy.spacy"
            val_file = self.config.preprocessed_dir / "spacy" / "val_spacy.spacy"
            output_dir = self.config.models_dir / "spacy_ner"

            if not train_file.exists():
                self.log("Training data not found, skipping spaCy training", "warning")
                self.results["train_spacy"] = {"status": "skipped"}
                return True

            self.log("Starting spaCy NER training...")

            model_path = train_spacy_ner(
                train_file=str(train_file),
                val_file=str(val_file),
                output_dir=str(output_dir),
                n_iter=self.config.spacy_config["n_iter"],
            )

            self.log(f"✅ spaCy model saved to {model_path}")
            self.results["train_spacy"] = {
                "status": "success",
                "model_path": str(model_path),
            }

            return True

        except Exception as e:
            self.log(f"❌ spaCy training failed: {e}", "error")
            self.results["train_spacy"] = {"status": "failed", "error": str(e)}
            return False

    def step_train_transformer(self):
        """Step 3: Train Transformer Model"""
        self.log("=" * 70)
        self.log("STEP 3: TRAIN TRANSFORMER MODEL")
        self.log("=" * 70)

        try:
            from training_transformer import TransformerConfig, TransformerTrainer

            train_file = (
                self.config.preprocessed_dir / "transformer" / "train_transformer.json"
            )
            val_file = (
                self.config.preprocessed_dir / "transformer" / "val_transformer.json"
            )

            if not train_file.exists():
                self.log(
                    "Training data not found, skipping Transformer training", "warning"
                )
                self.results["train_transformer"] = {"status": "skipped"}
                return True

            self.log("Starting Transformer training...")

            config = TransformerConfig(
                model_name=self.config.transformer_config["model_name"],
                num_epochs=self.config.transformer_config["num_epochs"],
                batch_size=self.config.transformer_config["batch_size"],
                output_dir=str(self.config.models_dir / "transformer_formula_mapper"),
            )

            trainer = TransformerTrainer(config)
            trainer.prepare_model()

            train_data, val_data = trainer.load_data(str(train_file), str(val_file))

            self.log(f"Training samples: {len(train_data)}")
            self.log(f"Validation samples: {len(val_data)}")

            train_result = trainer.train(train_data, val_data)

            self.log("✅ Transformer training complete")
            self.results["train_transformer"] = {
                "status": "success",
                "model_path": config.output_dir,
            }

            return True

        except Exception as e:
            self.log(f"❌ Transformer training failed: {e}", "error")
            self.results["train_transformer"] = {"status": "failed", "error": str(e)}
            return False

    def step_train_rag(self):
        """Step 4: Train RAG Model"""
        self.log("=" * 70)
        self.log("STEP 4: TRAIN RAG MODEL")
        self.log("=" * 70)

        try:
            from training_rag import RAGConfig, RAGTrainer

            train_file = self.config.preprocessed_dir / "mapping" / "train_mapping.json"

            if not train_file.exists():
                self.log("Training data not found, skipping RAG training", "warning")
                self.results["train_rag"] = {"status": "skipped"}
                return True

            self.log("Starting RAG training...")

            config = RAGConfig(
                embedding_model=self.config.rag_config["embedding_model"],
                top_k=self.config.rag_config["top_k"],
                output_dir=str(self.config.models_dir / "rag_formula_mapper"),
            )

            trainer = RAGTrainer(config)

            examples = trainer.load_data(str(train_file))
            self.log(f"Loaded {len(examples)} training examples")

            trainer.build_index(examples)
            trainer.save_model()

            self.log("✅ RAG training complete")
            self.results["train_rag"] = {
                "status": "success",
                "model_path": config.output_dir,
                "num_examples": len(examples),
            }

            return True

        except Exception as e:
            self.log(f"❌ RAG training failed: {e}", "error")
            self.results["train_rag"] = {"status": "failed", "error": str(e)}
            return False

    def step_train_llm(self):
        """Step 5: Setup LLM Integration"""
        self.log("=" * 70)
        self.log("STEP 5: SETUP LLM INTEGRATION")
        self.log("=" * 70)

        # Check for API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if not openai_key and not anthropic_key:
            self.log("No LLM API keys found, skipping LLM setup", "warning")
            self.results["train_llm"] = {"status": "skipped", "reason": "no_api_keys"}
            return True

        try:
            from training_llm import LLMConfig, LLMTrainer

            train_file = self.config.preprocessed_dir / "mapping" / "train_mapping.json"

            if not train_file.exists():
                self.log("Training data not found, skipping LLM setup", "warning")
                self.results["train_llm"] = {"status": "skipped"}
                return True

            self.log("Setting up LLM trainer...")

            provider = "openai" if openai_key else "anthropic"

            config = LLMConfig(
                provider=provider,
                model="gpt-4" if provider == "openai" else "claude-3-opus-20240229",
                output_dir=str(self.config.models_dir / "llm_formula_mapper"),
            )

            trainer = LLMTrainer(config)
            trainer.load_examples(str(train_file))

            self.log(f"✅ LLM integration ready ({provider})")
            self.results["train_llm"] = {
                "status": "success",
                "provider": provider,
                "num_examples": len(trainer.examples),
            }

            return True

        except Exception as e:
            self.log(f"❌ LLM setup failed: {e}", "error")
            self.results["train_llm"] = {"status": "failed", "error": str(e)}
            return False

    def step_evaluate_all(self):
        """Step 6: Evaluate All Models"""
        self.log("=" * 70)
        self.log("STEP 6: EVALUATE ALL MODELS")
        self.log("=" * 70)

        try:
            from evaluation_unified import ComparisonReport, ModelEvaluator

            test_file = self.config.preprocessed_dir / "mapping" / "test_mapping.json"

            if not test_file.exists():
                self.log("Test data not found, creating sample test set", "warning")
                self._create_sample_test_data()

            evaluator = ModelEvaluator()
            report = ComparisonReport()

            # Load test data
            with open(test_file, "r") as f:
                test_data = json.load(f)

            self.log(f"Evaluating on {len(test_data)} test examples")

            # Convert to prediction format for evaluation
            predictions = []
            for item in test_data:
                if isinstance(item, list):
                    predictions.append(
                        {"description": item[0], "true": item[1], "predicted": item[1]}
                    )  # Placeholder
                elif isinstance(item, dict):
                    predictions.append(
                        {
                            "description": item.get(
                                "description", item.get("input_text", "")
                            ),
                            "true": item.get("formula", item.get("target_text", "")),
                            "predicted": item.get(
                                "formula", item.get("target_text", "")
                            ),
                        }
                    )

            # Evaluate ensemble (always available)
            self.log("Evaluating Ensemble model...")
            from mapping_plus import EnhancedMapDescriptionToFormula, MappingContext

            context = MappingContext()
            mapper = EnhancedMapDescriptionToFormula(context)

            ensemble_predictions = []
            for pred in predictions:
                desc = pred["description"]
                result = mapper.map(desc, strategy="ensemble")
                ensemble_predictions.append(
                    {"description": desc, "true": pred["true"], "predicted": result}
                )

            ensemble_metrics = evaluator.evaluate_predictions(ensemble_predictions)
            report.add_model_results("Ensemble", ensemble_metrics)

            # Generate report
            self.log("Generating evaluation report...")

            report_path = self.config.results_dir / "evaluation_report.txt"
            plot_path = self.config.results_dir / "evaluation_plot.png"

            report.save_report(str(report_path))
            report.plot_comparison(str(plot_path))

            self.log("✅ Evaluation complete")
            self.results["evaluate_all"] = {
                "status": "success",
                "report_path": str(report_path),
                "plot_path": str(plot_path),
            }

            return True

        except Exception as e:
            self.log(f"❌ Evaluation failed: {e}", "error")
            self.results["evaluate_all"] = {"status": "failed", "error": str(e)}
            return False

    def step_deploy(self):
        """Step 7: Deploy Models"""
        self.log("=" * 70)
        self.log("STEP 7: DEPLOY MODELS")
        self.log("=" * 70)

        try:
            from deployment_pipeline import DeploymentAPI, DeploymentConfig
            from mapping_plus import EnhancedMapDescriptionToFormula, MappingContext

            self.log("Setting up deployment API...")

            deploy_config = DeploymentConfig(
                model_dir=str(self.config.models_dir), api_port=5000
            )

            api = DeploymentAPI(deploy_config)

            # Register ensemble mapper (always available)
            context = MappingContext()
            mapper = EnhancedMapDescriptionToFormula(context)
            api.registry.register_ensemble_mapper("ensemble", mapper)

            # Register other models if available
            spacy_model_path = self.config.models_dir / "spacy_ner" / "model-best"
            if spacy_model_path.exists():
                api.registry.register_spacy_model("ner", str(spacy_model_path))

            transformer_model_path = (
                self.config.models_dir / "transformer_formula_mapper"
            )
            if transformer_model_path.exists():
                api.registry.register_transformer_model(
                    "transformer", str(transformer_model_path)
                )

            rag_model_path = self.config.models_dir / "rag_formula_mapper"
            if rag_model_path.exists():
                api.registry.register_rag_model("rag", str(rag_model_path))

            self.log(f"Models registered: {api.registry.list_models()}")

            # Save deployment info
            deployment_info = {
                "timestamp": datetime.now().isoformat(),
                "models": api.registry.list_models(),
                "api_host": deploy_config.api_host,
                "api_port": deploy_config.api_port,
            }

            with open(self.config.results_dir / "deployment_info.json", "w") as f:
                json.dump(deployment_info, f, indent=2)

            self.log("✅ Deployment setup complete")
            self.log(f"To start API: python deployment_pipeline.py")

            self.results["deploy"] = {
                "status": "success",
                "models_deployed": api.registry.list_models(),
                "api_port": deploy_config.api_port,
            }

            return True

        except Exception as e:
            self.log(f"❌ Deployment failed: {e}", "error")
            self.results["deploy"] = {"status": "failed", "error": str(e)}
            return False

    def _create_sample_data(self):
        """Create sample training data"""
        sample_data = [
            {
                "description": "average of Sales",
                "formula": "AVG([Sales])",
                "entities": [
                    {"text": "average", "label": "OPER", "start": 0, "end": 7},
                    {"text": "Sales", "label": "TARGET", "start": 11, "end": 16},
                ],
            },
            {
                "description": "sum of Revenue by Region",
                "formula": "SUM([Revenue]) GROUP BY [Region]",
                "entities": [
                    {"text": "sum", "label": "OPER", "start": 0, "end": 3},
                    {"text": "Revenue", "label": "TARGET", "start": 7, "end": 14},
                    {"text": "Region", "label": "GROUPBY", "start": 18, "end": 24},
                ],
            },
            {
                "description": "count unique customers",
                "formula": "COUNTD([Customer])",
                "entities": [
                    {"text": "count", "label": "OPER", "start": 0, "end": 5},
                    {"text": "unique", "label": "OPER", "start": 6, "end": 12},
                    {"text": "customers", "label": "TARGET", "start": 13, "end": 22},
                ],
            },
            {
                "description": "maximum price per category",
                "formula": "MAX([Price]) GROUP BY [Category]",
                "entities": [
                    {"text": "maximum", "label": "OPER", "start": 0, "end": 7},
                    {"text": "price", "label": "TARGET", "start": 8, "end": 13},
                    {"text": "category", "label": "GROUPBY", "start": 18, "end": 26},
                ],
            },
            {
                "description": "total quantity sold",
                "formula": "SUM([Quantity])",
                "entities": [
                    {"text": "total", "label": "OPER", "start": 0, "end": 5},
                    {"text": "quantity", "label": "TARGET", "start": 6, "end": 14},
                ],
            },
        ]

        with open(self.config.raw_data_file, "w") as f:
            json.dump(sample_data, f, indent=2)

        self.log(f"Created sample data: {self.config.raw_data_file}")

    def _create_sample_test_data(self):
        """Create sample test data"""
        test_data = [
            ["average of Profit", "AVG([Profit])"],
            ["sum of Cost by Year", "SUM([Cost]) GROUP BY [Year]"],
            ["count of orders", "COUNT([Order ID])"],
        ]

        test_file = self.config.preprocessed_dir / "mapping" / "test_mapping.json"
        test_file.parent.mkdir(parents=True, exist_ok=True)

        with open(test_file, "w") as f:
            json.dump(test_data, f, indent=2)

    def run_pipeline(self, steps: list = None):
        """Run complete pipeline"""
        self.start_time = datetime.now()

        steps_to_run = steps or self.config.steps

        self.log("\n" + "=" * 70)
        self.log("🚀 STARTING COMPLETE ML PIPELINE")
        self.log("=" * 70)
        self.log(f"Steps to execute: {', '.join(steps_to_run)}")
        self.log(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("=" * 70 + "\n")

        # Execute steps
        step_methods = {
            "prepare_data": self.step_prepare_data,
            "train_spacy": self.step_train_spacy,
            "train_transformer": self.step_train_transformer,
            "train_rag": self.step_train_rag,
            "train_llm": self.step_train_llm,
            "evaluate_all": self.step_evaluate_all,
            "deploy": self.step_deploy,
        }

        for step_name in steps_to_run:
            if step_name in step_methods:
                success = step_methods[step_name]()
                if not success:
                    self.log(f"❌ Pipeline failed at step: {step_name}", "error")
                    break
            else:
                self.log(f"⚠️  Unknown step: {step_name}", "warning")

        # Summary
        self.print_summary()

        # Save results
        self.save_results()

    def print_summary(self):
        """Print pipeline summary"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        self.log("\n" + "=" * 70)
        self.log("📊 PIPELINE SUMMARY")
        self.log("=" * 70)
        self.log(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Duration: {duration}")
        self.log("=" * 70)

        self.log("\nStep Results:")
        for step_name, result in self.results.items():
            status = result.get("status", "unknown")
            status_icon = (
                "✅" if status == "success" else "❌" if status == "failed" else "⏭️"
            )
            self.log(f"  {status_icon} {step_name}: {status}")

            if "error" in result:
                self.log(f"      Error: {result['error']}")

        self.log("=" * 70)

        # Check overall success
        failed_steps = [
            name
            for name, result in self.results.items()
            if result.get("status") == "failed"
        ]

        if failed_steps:
            self.log(
                f"\n❌ Pipeline completed with {len(failed_steps)} failed step(s)",
                "error",
            )
        else:
            self.log("\n✅ Pipeline completed successfully!")

        self.log("=" * 70 + "\n")

    def save_results(self):
        """Save pipeline results"""
        results_file = (
            self.config.results_dir
            / f"pipeline_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        full_results = {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration": str(datetime.now() - self.start_time),
            "steps": self.results,
        }

        with open(results_file, "w") as f:
            json.dump(full_results, f, indent=2)

        self.log(f"Results saved to: {results_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run complete ML pipeline")
    parser.add_argument(
        "--steps",
        nargs="+",
        choices=[
            "prepare_data",
            "train_spacy",
            "train_transformer",
            "train_rag",
            "train_llm",
            "evaluate_all",
            "deploy",
        ],
        help="Specific steps to run (default: all steps)",
    )
    parser.add_argument(
        "--skip-training",
        action="store_true",
        help="Skip all training steps (useful for testing)",
    )

    args = parser.parse_args()

    # Create configuration
    config = PipelineConfig()

    # Create executor
    executor = PipelineExecutor(config)

    # Determine steps to run
    if args.skip_training:
        steps = ["prepare_data", "evaluate_all", "deploy"]
    elif args.steps:
        steps = args.steps
    else:
        steps = None  # Run all steps

    # Run pipeline
    try:
        executor.run_pipeline(steps)
    except KeyboardInterrupt:
        executor.log("\n⚠️  Pipeline interrupted by user", "warning")
    except Exception as e:
        executor.log(f"\n❌ Pipeline failed with error: {e}", "error")
        raise


if __name__ == "__main__":
    main()
