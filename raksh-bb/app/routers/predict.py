from fastapi import APIRouter
from ..schemas import PredictionRequest, PredictionResponse
from ..ml_models import predict_from_models, MODEL_VERSION

router = APIRouter(prefix="/predict", tags=["predict"])


@router.post("/", response_model=PredictionResponse)
def predict_feasibility(payload: PredictionRequest):
    # Adapt this line to your actual ml_models return type
    # Option A: if predict_from_models returns (feasible, depth)
    feasible, depth = predict_from_models(lat=payload.latitude, lon=payload.longitude)

    # Option B: if it returns a dict:
    # res = predict_from_models(lat=payload.latitude, lon=payload.longitude)
    # feasible = bool(res["feasible"])
    # depth = float(res["depth"])

    return PredictionResponse(
        latitude=payload.latitude,
        longitude=payload.longitude,
        predicted_feasible=bool(feasible),
        predicted_depth_m=float(depth),
        model_version=MODEL_VERSION,
    )
