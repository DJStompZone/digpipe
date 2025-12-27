"""Command Line Interface for DigPipe."""

import argparse
import sys
from . import pipeline

def main():
    parser = argparse.ArgumentParser(description="DigPipe: Modular Decimal-Digit Input Pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Generate Command
    gen_parser = subparsers.add_parser("generate", help="Generate digits to tape")
    gen_parser.add_argument("--source", default="pi", help="Digit source (default: pi)")
    gen_parser.add_argument("--digits", type=int, required=True, help="Total digits to generate")
    gen_parser.add_argument("--chunk-size", type=int, default=1000000, help="Digits per chunk")
    gen_parser.add_argument("--out", required=True, help="Output directory for tape")
    
    # Render Command
    render_parser = subparsers.add_parser("render", help="Render tape to inputs")
    render_parser.add_argument("--tape", required=True, help="Path to input tape directory")
    render_parser.add_argument("--mapper", default="gba-tenkey", help="Mapper to use")
    render_parser.add_argument("--sink", default="frame-log", help="Sink to use")
    render_parser.add_argument("--start-chunk", type=int, default=0, help="Start rendering from this chunk index")
    render_parser.add_argument("--out", default="-", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    try:
        if args.command == "generate":
            pipeline.run_generation(
                source_name=args.source,
                total_digits=args.digits,
                chunk_size=args.chunk_size,
                tape_path=args.out
            )
        elif args.command == "render":
            pipeline.run_rendering(
                tape_path=args.tape,
                mapper_name=args.mapper,
                sink_name=args.sink,
                output_path=args.out,
                start_chunk=args.start_chunk
            )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
