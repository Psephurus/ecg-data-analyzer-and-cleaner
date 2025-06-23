import argparse
import logging

from ecg.config import load_config
from ecg.pipeline import ECGProcessor


def main():
    parser = argparse.ArgumentParser(description="ECG R-peak detection and RR analysis")
    parser.add_argument("filepath", type=str, nargs="?", default="../data/20250521/10 min.txt",
                        help="Path to ECG txt file")
    parser.add_argument("--config", type=str, default="config.yml",
                        help="Path to configuration file")
    parser.add_argument("--fs", type=int, default=500, help="Sampling rate (Hz)")
    parser.add_argument("--max-diff", type=float, default=1.0,
                        help="Maximum allowed difference between adjacent RR intervals (in seconds)")
    parser.add_argument("--min-rr", type=float, default=0.0,
                        help="Minimum allowed RR interval (in seconds)")
    parser.add_argument("--out-dir", type=str, default="out",
                        help="Output directory")
    parser.add_argument("--plot-ecg", action="store_true",
                        help="Plot ECG with R peaks and save as image")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    cfg = load_config(args.config)

    cli_params = {
        k: v
        for k, v in vars(args).items()
        if k in ["fs", "max_diff", "min_rr", "lowcut", "highcut", "order"] and v is not None
    }
    cfg.update(cli_params)

    processor = ECGProcessor(**cfg)
    processor.process_file(args.filepath)


if __name__ == "__main__":
    main()