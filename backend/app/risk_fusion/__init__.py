"""UPI Guardian - Multi-Signal Risk Fusion Engine.

Phase 6 implementation combining Isolation Forest transaction anomalies,
NLP communication scam classifications, behavioral deviations, payee novelty,
velocity, and temporal correlation into an explainable composite risk score.
"""

from app.risk_fusion.config import RiskFusionConfig
from app.risk_fusion.inference import RiskFusionService

__all__ = ["RiskFusionConfig", "RiskFusionService"]
