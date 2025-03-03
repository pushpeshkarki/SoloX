from solox.public.apm import AppPerformanceMonitor
from solox.analytics.performance_analyzer import PerformanceAnalyzer
from solox.analytics.data_collector import PerformanceDataCollector
import pandas as pd
import plotly.io as pio
import os
from datetime import datetime

def main():
    # Initialize performance monitoring
    apm = AppPerformanceMonitor(
        pkgName='com.example.app',
        platform='Android',
        deviceId='your_device_id',
        surfaceview=True,
        noLog=False
    )
    
    # Initialize data collector
    collector = PerformanceDataCollector(apm)
    
    # Collect metrics for 5 minutes
    print("Collecting performance metrics...")
    metrics_df = collector.collect_metrics(duration=300, interval=1.0)
    
    # Save raw metrics
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metrics_file = f"performance_metrics_{timestamp}.csv"
    collector.save_metrics(metrics_file)
    print(f"Saved raw metrics to {metrics_file}")
    
    # Initialize performance analyzer
    analyzer = PerformanceAnalyzer(sensitivity=0.1)
    
    # Generate comprehensive analysis
    print("\nGenerating performance analysis...")
    analysis = analyzer.generate_analysis_report(metrics_df)
    
    # Print anomalies
    print("\nDetected Anomalies:")
    for metric, indices in analysis['anomalies'].items():
        print(f"{metric}: {len(indices)} anomalies detected")
        if indices:
            print(f"Anomaly timestamps: {metrics_df.iloc[indices]['timestamp'].tolist()}")
    
    # Print correlations
    print("\nMetric Correlations:")
    correlation_df = pd.DataFrame(analysis['correlations'])
    print(correlation_df)
    
    # Print predictions from both Prophet and LSTM
    print("\nPerformance Predictions:")
    for metric in analysis['predictions'].keys():
        prophet_forecast = analysis['predictions'][metric]
        lstm_forecast = analysis['lstm_predictions'][metric]
        last_value = metrics_df[metric].iloc[-1]
        
        print(f"\n{metric}:")
        print(f"  Current value: {last_value:.2f}")
        
        # Prophet predictions
        predicted_next = prophet_forecast['forecast']['yhat'][-1]
        print(f"  Prophet Forecast: {predicted_next:.2f}")
        print(f"  Prophet CI: [{prophet_forecast['confidence_interval']['lower'][-1]:.2f}, "
              f"{prophet_forecast['confidence_interval']['upper'][-1]:.2f}]")
        
        # LSTM predictions
        lstm_next = lstm_forecast[0]
        print(f"  LSTM Forecast: {lstm_next:.2f}")
        
        # Compare predictions
        print(f"  Prediction Difference: {abs(predicted_next - lstm_next):.2f}")
    
    # Save plots
    if not os.path.exists('analysis_plots'):
        os.makedirs('analysis_plots')
    
    for name, fig in analysis['plots'].items():
        plot_file = f"analysis_plots/{name}_{timestamp}.html"
        pio.write_html(fig, plot_file)
        print(f"\nSaved {name} plot to {plot_file}")
    
    # Example of performance regression detection
    try:
        baseline_metrics = pd.read_csv("baseline_metrics.csv")
        regressions = analyzer.detect_performance_regression(
            baseline_metrics,
            metrics_df,
            threshold=0.1
        )
        
        if regressions:
            print("\nPerformance Regressions Detected:")
            for metric, regression_pct in regressions.items():
                print(f"{metric}: {regression_pct:.2%} regression")
        else:
            print("\nNo significant performance regressions detected")
    except FileNotFoundError:
        print("\nNo baseline metrics found. Current metrics will be saved as baseline.")
        metrics_df.to_csv("baseline_metrics.csv", index=False)

if __name__ == "__main__":
    main() 