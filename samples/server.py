import asyncio
from pydantic import BaseModel
from typing import Dict, Any

class MetricResponse(BaseModel):
    cpu: float
    memory: float
    latency: float

class ClusterService:
    def __init__(self, cluster_name: str):
        self.cluster_name = cluster_name

    async def get_system_telemetry(self) -> MetricResponse:
        # Simulate non-blocking asynchronous metric collection
        await asyncio.sleep(0.01)
        return MetricResponse(cpu=0.985, memory=42.4, latency=12.8)

# Simulating API Router
async def handle_metrics_route() -> Dict[str, Any]:
    service = ClusterService("us-east-prod")
    telemetry = await service.get_system_telemetry()
    return telemetry.model_dump()
