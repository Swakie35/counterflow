import argparse
from .pipeline import save_demo

def main():
    parser=argparse.ArgumentParser(description='Run a seeded walk-forward demand forecast benchmark')
    parser.add_argument('--report',default='reports/generated/validation.json')
    args=parser.parse_args(); metrics=save_demo(args.report)
    print(f"Model MAE: {metrics['mean_model_mae']}; weekly naive MAE: {metrics['mean_baseline_mae']}")
    print(f"Saved fold-by-fold validation to {args.report}")

if __name__=='__main__':main()
