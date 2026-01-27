"""Health Monitor for Sync Service - External Architecture.

Monitors sync service health and restarts if it stops.
Can be integrated into daemon or run as separate service.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import subprocess
import time
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class SyncHealthMonitor:
    """Health monitor for sync service.
    
    Monitors sync service health and restarts if it stops.
    Provides external architecture for ensuring service availability.
    """
    
    def __init__(
        self,
        check_interval: int = 60,  # Check every minute
        restart_on_failure: bool = True,
        max_restart_attempts: int = 5,
        restart_cooldown: int = 300,  # 5 minutes between restarts
    ) -> None:
        """Initialize health monitor.
        
        Args:
            check_interval: How often to check health (seconds)
            restart_on_failure: Whether to restart on failure
            max_restart_attempts: Maximum restart attempts before giving up
            restart_cooldown: Seconds to wait between restart attempts
        """
        self.check_interval = check_interval
        self.restart_on_failure = restart_on_failure
        self.max_restart_attempts = max_restart_attempts
        self.restart_cooldown = restart_cooldown
        
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.last_restart_attempt: Optional[datetime] = None
        self.restart_count = 0
        
        # Paths
        project_root = Path(__file__).parent.parent.parent.parent
        self.pid_file = project_root / "data" / "local" / "sync_service.pid"
        self.start_script = project_root / "scripts" / "start_sync_service.sh"
        self.log_file = project_root / "sync_health_monitor.log"
    
    def start(self) -> None:
        """Start health monitor."""
        if self.running:
            logger.warning("Health monitor already running")
            return
        
        logger.info("=" * 60)
        logger.info("STARTING SYNC HEALTH MONITOR")
        logger.info("=" * 60)
        logger.info(f"Check interval: {self.check_interval} seconds")
        logger.info(f"Restart on failure: {self.restart_on_failure}")
        logger.info("")
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("✅ Health monitor started")
        logger.info("   Monitoring sync service health")
        logger.info("   Will restart if service stops")
    
    def stop(self) -> None:
        """Stop health monitor."""
        logger.info("Stopping health monitor...")
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        logger.info("✅ Health monitor stopped")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            try:
                is_healthy = self.check_health()
                
                if not is_healthy and self.restart_on_failure:
                    self._attempt_restart()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitor loop: {e}", exc_info=True)
                time.sleep(self.check_interval)
    
    def check_health(self) -> bool:
        """Check if sync service is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Check PID file
            if not self.pid_file.exists():
                logger.warning("Sync service PID file not found")
                return False
            
            pid = int(self.pid_file.read_text().strip())
            
            # Check if process is running
            try:
                # Use ps to check if process exists
                result = subprocess.run(
                    ["ps", "-p", str(pid)],
                    capture_output=True,
                    timeout=5,
                )
                
                if result.returncode == 0:
                    logger.debug(f"Sync service healthy (PID: {pid})")
                    return True
                else:
                    logger.warning(f"Sync service process not found (PID: {pid})")
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.warning("Health check timed out")
                return False
            except Exception as e:
                logger.warning(f"Health check error: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to check health: {e}", exc_info=True)
            return False
    
    def _attempt_restart(self) -> None:
        """Attempt to restart sync service."""
        # Check cooldown
        if self.last_restart_attempt:
            elapsed = (datetime.utcnow() - self.last_restart_attempt).total_seconds()
            if elapsed < self.restart_cooldown:
                logger.debug(f"Restart cooldown active ({elapsed:.0f}s / {self.restart_cooldown}s)")
                return
        
        # Check max attempts
        if self.restart_count >= self.max_restart_attempts:
            logger.error(
                f"Max restart attempts ({self.max_restart_attempts}) reached. "
                "Manual intervention required."
            )
            return
        
        logger.warning("Sync service unhealthy - attempting restart...")
        
        try:
            # Remove stale PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            
            # Run start script
            result = subprocess.run(
                [str(self.start_script)],
                capture_output=True,
                timeout=30,
                cwd=self.start_script.parent.parent,
            )
            
            if result.returncode == 0:
                logger.info("✅ Sync service restarted successfully")
                self.restart_count = 0  # Reset on success
            else:
                logger.error(f"Failed to restart sync service: {result.stderr.decode()}")
                self.restart_count += 1
                self.last_restart_attempt = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"Error restarting sync service: {e}", exc_info=True)
            self.restart_count += 1
            self.last_restart_attempt = datetime.utcnow()
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitor status.
        
        Returns:
            Status dictionary
        """
        return {
            "running": self.running,
            "service_healthy": self.check_health(),
            "restart_count": self.restart_count,
            "last_restart_attempt": self.last_restart_attempt.isoformat() if self.last_restart_attempt else None,
            "check_interval": self.check_interval,
        }
