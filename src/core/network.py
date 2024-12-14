import ping3
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PingResult:
    timestamp: datetime
    server: str
    ping_time: float
    is_connected: bool
    status: str

class NetworkChecker:
    def __init__(self):
        self.timeout = 1.0

    def check(self, server: str) -> PingResult:
        try:
            ping_time = ping3.ping(server, timeout=self.timeout)
            is_connected = ping_time is not None
            status = "Connected" if is_connected else "Connection Lost"
            
            if is_connected:
                ping_time = round(ping_time * 1000, 2)
            else:
                ping_time = float('nan')

            return PingResult(
                timestamp=datetime.now(),
                server=server,
                ping_time=ping_time,
                is_connected=is_connected,
                status=status
            )
        except Exception as e:
            return PingResult(
                timestamp=datetime.now(),
                server=server,
                ping_time=float('nan'),
                is_connected=False,
                status=f"Error: {str(e)}"
            )
