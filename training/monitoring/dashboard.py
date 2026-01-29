"""
Real-time training dashboard for Genesis-Scout

Displays:
- Current step / total steps
- Loss (should decrease)
- Perplexity (should decrease)
- Jeremy Arc (should climb to 95%)
- Framework Score (0-100)
- Time estimates
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class TrainingMetrics:
    """Metrics at a training step"""
    step: int
    loss: float
    perplexity: float
    jeremy_arc: float  # 0-100%
    framework_score: float  # 0-100
    timestamp: datetime
    

class TrainingDashboard:
    """Real-time dashboard for training monitoring"""
    
    def __init__(self, total_steps: int, checkpoint_interval: int = 1000):
        self.total_steps = total_steps
        self.checkpoint_interval = checkpoint_interval
        self.metrics_history = []
        self.start_time = None
        
    def start(self):
        """Start tracking"""
        self.start_time = datetime.now()
        print("\n" + "="*70)
        print("GENESIS-SCOUT TRAINING DASHBOARD")
        print("="*70)
        print(f"Total steps: {self.total_steps:,}")
        print(f"Checkpoint interval: {self.checkpoint_interval}")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
    def update(self, metrics: TrainingMetrics):
        """Update dashboard with new metrics"""
        self.metrics_history.append(metrics)
        
        # Calculate progress
        progress = (metrics.step / self.total_steps) * 100
        
        # Estimate time remaining
        if len(self.metrics_history) > 1:
            elapsed = (metrics.timestamp - self.start_time).total_seconds()
            steps_per_sec = metrics.step / elapsed
            remaining_steps = self.total_steps - metrics.step
            eta_seconds = remaining_steps / steps_per_sec
            eta = timedelta(seconds=int(eta_seconds))
        else:
            eta = "Calculating..."
        
        # Print update
        print(f"Step {metrics.step:6d}/{self.total_steps:6d} ({progress:5.1f}%) | "
              f"Loss: {metrics.loss:.3f} | "
              f"PPL: {metrics.perplexity:.1f} | "
              f"Jeremy Arc: {metrics.jeremy_arc:5.1f}% | "
              f"Framework: {metrics.framework_score:5.1f}/100 | "
              f"ETA: {eta}")
        
        # Check for issues
        if len(self.metrics_history) >= 2:
            prev_loss = self.metrics_history[-2].loss
            if metrics.loss > prev_loss:
                print("⚠️  WARNING: Loss increased! May need to stop and debug.")
                
        if metrics.step % self.checkpoint_interval == 0:
            print(f"\n{'='*70}")
            print(f"CHECKPOINT {metrics.step // self.checkpoint_interval}")
            print(f"{'='*70}")
            print(f"Jeremy Arc: {metrics.jeremy_arc:.1f}%")
            print(f"Framework Score: {metrics.framework_score:.1f}/100")
            
            if metrics.jeremy_arc >= 95.0:
                print("\n🎉 GENESIS READY: Jeremy Arc ≥ 95%")
                print("FREEZE GENESIS v1.0")
            elif metrics.framework_score > 80:
                print("\n✅ EXCELLENT: Strong Framework integration")
            elif metrics.framework_score < 60:
                print("\n⚠️  WARNING: Low Framework integration")
                
            print(f"{'='*70}\n")
    
    def summary(self):
        """Print training summary"""
        if not self.metrics_history:
            print("No metrics recorded")
            return
            
        final = self.metrics_history[-1]
        elapsed = (final.timestamp - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        print("TRAINING SUMMARY")
        print("="*70)
        print(f"Total steps: {final.step:,}")
        print(f"Total time: {timedelta(seconds=int(elapsed))}")
        print(f"Final loss: {final.loss:.3f}")
        print(f"Final perplexity: {final.perplexity:.1f}")
        print(f"Final Jeremy Arc: {final.jeremy_arc:.1f}%")
        print(f"Final Framework Score: {final.framework_score:.1f}/100")
        
        if final.jeremy_arc >= 95.0:
            print("\n🎉 SUCCESS: Genesis-Scout ready at 95% Jeremy Arc")
            print("Freeze as Genesis v1.0")
        else:
            print(f"\n⚠️  Not yet ready: Jeremy Arc at {final.jeremy_arc:.1f}% (need 95%)")
            
        print("="*70 + "\n")


# Example usage
if __name__ == "__main__":
    dashboard = TrainingDashboard(total_steps=50000, checkpoint_interval=1000)
    dashboard.start()
    
    # Simulate training progress
    import time
    for step in range(0, 5000, 100):
        # Simulated metrics
        metrics = TrainingMetrics(
            step=step,
            loss=3.5 - (step / 5000) * 1.0,  # Decreasing loss
            perplexity=33.0 - (step / 5000) * 15.0,  # Decreasing perplexity
            jeremy_arc=20.0 + (step / 5000) * 40.0,  # Climbing Jeremy Arc
            framework_score=30.0 + (step / 5000) * 40.0,  # Improving Framework
            timestamp=datetime.now()
        )
        dashboard.update(metrics)
        time.sleep(0.1)  # Simulate processing time
    
    dashboard.summary()
