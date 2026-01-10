#!/usr/bin/python3
"""
Batch Processing for Formula Generation
Process large batches of descriptions efficiently
"""

import json
import logging
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from tqdm import tqdm


@dataclass
class BatchConfig:
    """Configuration for batch processing"""

    input_file: str
    output_file: str
    model_type: str = "ensemble"
    model_path: Optional[str] = None
    batch_size: int = 32
    num_workers: int = 4
    use_multiprocessing: bool = False
    save_intermediate: bool = True
    intermediate_interval: int = 100


class BatchProcessor:
    """Process descriptions in batches"""

    def __init__(self, config: BatchConfig):
        self.config = config
        self.model = None
        self.results = []

        # Setup logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)

        # Load model
        self._load_model()

    def _load_model(self):
        """Load the specified model"""
        model_type = self.config.model_type

        self.logger.info(f"Loading {model_type} model...")

        if model_type == "ensemble":
            from mapping_plus import EnhancedMapDescriptionToFormula, MappingContext

            context = MappingContext()
            self.model = EnhancedMapDescriptionToFormula(context)
            self.logger.info("✅ Ensemble model loaded")

        elif model_type == "transformer":
            import torch
            from transformers import AutoTokenizer, T5ForConditionalGeneration

            model_path = self.config.model_path or "./models/transformer_formula_mapper"

            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = T5ForConditionalGeneration.from_pretrained(model_path)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(self.device)

            self.logger.info(f"✅ Transformer model loaded on {self.device}")

        elif model_type == "rag":
            from training_rag import RAGConfig, RAGTrainer

            model_path = self.config.model_path or "./models/rag_formula_mapper"

            rag_config = RAGConfig()
            self.model = RAGTrainer(rag_config)
            self.model.load_model(model_path)

            self.logger.info("✅ RAG model loaded")

        elif model_type == "spacy":
            import spacy

            model_path = self.config.model_path or "./models/spacy_ner/model-best"
            self.model = spacy.load(model_path)

            self.logger.info("✅ spaCy NER model loaded")

        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def load_input(self) -> List[Dict]:
        """Load input descriptions"""
        input_path = Path(self.config.input_file)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        self.logger.info(f"Loading input from {input_path}")

        # Support multiple formats
        if input_path.suffix == ".json":
            with open(input_path, "r") as f:
                data = json.load(f)

        elif input_path.suffix == ".csv":
            df = pd.read_csv(input_path)
            data = df.to_dict("records")

        elif input_path.suffix == ".txt":
            with open(input_path, "r") as f:
                lines = f.readlines()
            data = [{"description": line.strip()} for line in lines if line.strip()]

        else:
            raise ValueError(f"Unsupported file format: {input_path.suffix}")

        self.logger.info(f"Loaded {len(data)} descriptions")
        return data

    def process_single(self, item: Dict) -> Dict:
        """Process single description"""
        description = item.get("description", item.get("text", ""))

        try:
            if self.config.model_type == "ensemble":
                result = self.model.map_with_all_candidates(description)

                return {
                    "description": description,
                    "formula": result["best_formula"],
                    "strategy": result["best_strategy"],
                    "confidence": result["confidence"],
                    "status": "success",
                }

            elif self.config.model_type == "transformer":
                import torch

                input_text = f"translate description to formula: {description}"
                inputs = self.tokenizer(
                    input_text, return_tensors="pt", max_length=128, truncation=True
                ).to(self.device)

                with torch.no_grad():
                    outputs = self.model.generate(
                        inputs.input_ids,
                        max_length=128,
                        num_beams=4,
                        early_stopping=True,
                    )

                formula = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

                return {
                    "description": description,
                    "formula": formula,
                    "confidence": 0.85,
                    "status": "success",
                }

            elif self.config.model_type == "rag":
                formula = self.model.generate_formula(description)

                return {
                    "description": description,
                    "formula": formula,
                    "confidence": 0.80,
                    "status": "success",
                }

            elif self.config.model_type == "spacy":
                doc = self.model(description)
                entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]

                return {
                    "description": description,
                    "entities": entities,
                    "status": "success",
                }

        except Exception as e:
            return {"description": description, "error": str(e), "status": "failed"}

    def process_batch(self, items: List[Dict]) -> List[Dict]:
        """Process batch of descriptions"""
        results = []

        for item in items:
            result = self.process_single(item)
            results.append(result)

        return results

    def process_parallel(self, data: List[Dict]) -> List[Dict]:
        """Process data in parallel"""
        results = []

        # Split into batches
        batches = [
            data[i : i + self.config.batch_size]
            for i in range(0, len(data), self.config.batch_size)
        ]

        self.logger.info(
            f"Processing {len(batches)} batches with {self.config.num_workers} workers"
        )

        # Choose executor
        Executor = (
            ProcessPoolExecutor
            if self.config.use_multiprocessing
            else ThreadPoolExecutor
        )

        with Executor(max_workers=self.config.num_workers) as executor:
            futures = [executor.submit(self.process_batch, batch) for batch in batches]

            # Process with progress bar
            for i, future in enumerate(tqdm(futures, desc="Processing batches")):
                batch_results = future.result()
                results.extend(batch_results)

                # Save intermediate results
                if (
                    self.config.save_intermediate
                    and (i + 1) % self.config.intermediate_interval == 0
                ):
                    self._save_intermediate(results, i + 1)

        return results

    def process_sequential(self, data: List[Dict]) -> List[Dict]:
        """Process data sequentially"""
        results = []

        self.logger.info(f"Processing {len(data)} items sequentially")

        for item in tqdm(data, desc="Processing"):
            result = self.process_single(item)
            results.append(result)

            # Save intermediate results
            if (
                self.config.save_intermediate
                and len(results) % self.config.intermediate_interval == 0
            ):
                self._save_intermediate(results, len(results))

        return results

    def _save_intermediate(self, results: List[Dict], count: int):
        """Save intermediate results"""
        output_path = Path(self.config.output_file)
        intermediate_path = (
            output_path.parent
            / f"{output_path.stem}_intermediate_{count}{output_path.suffix}"
        )

        self._save_results(results, str(intermediate_path))
        self.logger.info(
            f"Saved intermediate results ({count} items) to {intermediate_path}"
        )

    def _save_results(self, results: List[Dict], output_path: str):
        """Save results to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.suffix == ".json":
            with open(output_path, "w") as f:
                json.dump(results, f, indent=2)

        elif output_path.suffix == ".csv":
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)

        else:
            raise ValueError(f"Unsupported output format: {output_path.suffix}")

    def run(self):
        """Run batch processing"""
        start_time = time.time()

        self.logger.info("=" * 70)
        self.logger.info("BATCH PROCESSING STARTED")
        self.logger.info("=" * 70)

        # Load data
        data = self.load_input()

        # Process
        if self.config.num_workers > 1:
            results = self.process_parallel(data)
        else:
            results = self.process_sequential(data)

        # Save results
        self._save_results(results, self.config.output_file)

        # Summary
        duration = time.time() - start_time
        success_count = sum(1 for r in results if r.get("status") == "success")

        self.logger.info("=" * 70)
        self.logger.info("BATCH PROCESSING COMPLETED")
        self.logger.info("=" * 70)
        self.logger.info(f"Total items: {len(results)}")
        self.logger.info(f"Successful: {success_count}")
        self.logger.info(f"Failed: {len(results) - success_count}")
        self.logger.info(f"Duration: {duration:.2f} seconds")
        self.logger.info(f"Throughput: {len(results)/duration:.2f} items/second")


# Add to the END of deployment_batch.py


def create_sample_input():
    """Create sample input file for testing"""
    sample_data = [
        {"description": "average of Sales"},
        {"description": "sum of Revenue by Region"},
        {"description": "count unique customers"},
        {"description": "maximum price per category"},
        {"description": "total quantity sold"},
        {"description": "minimum discount"},
        {"description": "count of orders by month"},
        {"description": "average profit margin"},
        {"description": "sum of costs grouped by department"},
        {"description": "distinct product categories"},
    ]

    output_file = Path("./data/sample_batch_input.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(sample_data, f, indent=2)

    print(f"✅ Created sample input: {output_file}")
    return str(output_file)


def main():
    """Main entry point for batch processing"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch processing for formula generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process with ensemble model (default)
  python deployment_batch.py -i input.json -o output.json

  # Process with transformer model
  python deployment_batch.py -i input.json -o output.json -m transformer

  # Process with 8 workers in parallel
  python deployment_batch.py -i input.json -o output.json -w 8

  # Process with multiprocessing
  python deployment_batch.py -i input.json -o output.json -w 4 --multiprocessing

  # Create sample input file
  python deployment_batch.py --create-sample
        """,
    )

    parser.add_argument(
        "-i", "--input", type=str, help="Input file (JSON, CSV, or TXT)"
    )

    parser.add_argument("-o", "--output", type=str, help="Output file (JSON or CSV)")

    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="ensemble",
        choices=["ensemble", "transformer", "rag", "spacy"],
        help="Model type to use (default: ensemble)",
    )

    parser.add_argument(
        "-p",
        "--model-path",
        type=str,
        help="Path to model (if not using default location)",
    )

    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for processing (default: 32)",
    )

    parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)",
    )

    parser.add_argument(
        "--multiprocessing",
        action="store_true",
        help="Use multiprocessing instead of threading",
    )

    parser.add_argument(
        "--no-intermediate",
        action="store_true",
        help="Disable intermediate result saving",
    )

    parser.add_argument(
        "--intermediate-interval",
        type=int,
        default=100,
        help="Save intermediate results every N items (default: 100)",
    )

    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create sample input file for testing",
    )

    args = parser.parse_args()

    # Handle sample creation
    if args.create_sample:
        sample_file = create_sample_input()
        print(f"\nTo process the sample file, run:")
        print(
            f"python deployment_batch.py -i {sample_file} -o ./results/sample_output.json"
        )
        return

    # Validate required arguments
    if not args.input or not args.output:
        parser.error("Both --input and --output are required (or use --create-sample)")

    # Create configuration
    config = BatchConfig(
        input_file=args.input,
        output_file=args.output,
        model_type=args.model,
        model_path=args.model_path,
        batch_size=args.batch_size,
        num_workers=args.workers,
        use_multiprocessing=args.multiprocessing,
        save_intermediate=not args.no_intermediate,
        intermediate_interval=args.intermediate_interval,
    )

    # Run batch processing
    try:
        processor = BatchProcessor(config)
        processor.run()

        print("\n" + "=" * 70)
        print("✅ BATCH PROCESSING COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print(f"Output saved to: {args.output}")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo create a sample input file, run:")
        print("python deployment_batch.py --create-sample")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Batch processing failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
