"""FastAPI application for analytics with GPU support."""

import asyncio
from typing import List, Optional, Dict, Any
import numpy as np
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from modal import Image, gpu, method, Stub

# Models
class DataPoint(BaseModel):
    """Data point for analytics."""
    id: int
    value: float
    metadata: Optional[Dict[str, Any]] = {}

class AnalyticsRequest(BaseModel):
    """Request for analytics operation."""
    data: List[DataPoint]
    operation: str
    gpu_enabled: bool = True

class AnalyticsResponse(BaseModel):
    """Response from analytics operation."""
    result: float
    computation_time: float
    used_gpu: bool
    operation: str

# Modal setup
stub = Stub("analytics-platform")
app = FastAPI(title="Analytics Platform")

image = (
    Image.debian_slim()
    .pip_install(
        "numpy",
        "scikit-learn",
        "torch",
        "pandas",
        "fastapi",
        "uvicorn",
        "httpx",
        "pytest",
        "pytest-asyncio"
    )
)

@stub.cls(
    gpu=gpu.T4(),
    image=image
)
class GPUAnalytics:
    """GPU-accelerated analytics operations."""
    
    def __enter__(self):
        """Initialize GPU context."""
        import torch
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.torch = torch
        
    @method()
    def matrix_multiply(self, data: List[float]) -> float:
        """Perform matrix multiplication on GPU."""
        matrix = np.array(data).reshape(-1, 2)
        tensor = self.torch.tensor(matrix, device=self.device)
        result = self.torch.matmul(tensor, tensor.T)
        return float(result.mean().cpu().numpy())
    
    @method()
    def pca(self, data: List[float]) -> float:
        """Perform PCA on GPU."""
        matrix = np.array(data).reshape(-1, 2)
        tensor = self.torch.tensor(matrix, device=self.device)
        U, S, V = self.torch.pca_lowrank(tensor)
        return float(S[0].cpu().numpy())
    
    @method()
    def correlation(self, data: List[float]) -> float:
        """Calculate correlation on GPU."""
        matrix = np.array(data).reshape(-1, 2)
        tensor = self.torch.tensor(matrix, device=self.device)
        corr = self.torch.corrcoef(tensor.T)
        return float(corr[0, 1].cpu().numpy())
    
    @method()
    def mean(self, data: List[float]) -> float:
        """Calculate mean on GPU."""
        tensor = self.torch.tensor(data, device=self.device)
        return float(tensor.mean().cpu().numpy())

# FastAPI app
app = FastAPI(title="Analytics Platform")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to the Analytics Platform",
        "gpu_enabled": True,
        "supported_operations": [
            "mean",
            "correlation",
            "matrix_multiply",
            "pca"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    import torch
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available()
    }

@app.get("/data")
async def get_sample_data():
    """Get sample data for testing."""
    return [
        {
            "id": i,
            "value": float(np.random.randn()),
            "metadata": {"generated": True}
        }
        for i in range(10)
    ]

@app.post("/analyze")
async def analyze(request: AnalyticsRequest) -> AnalyticsResponse:
    """Perform analytics operation."""
    if not request.data:
        raise HTTPException(status_code=500, detail="Empty data")
    
    if request.operation not in ["mean", "correlation", "matrix_multiply", "pca"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported operation: {request.operation}"
        )
    
    # Extract values
    values = [d.value for d in request.data]
    
    # Initialize analytics
    analytics = GPUAnalytics()
    
    # Time the operation
    start_time = asyncio.get_event_loop().time()
    
    # Perform operation
    if request.operation == "mean":
        result = await analytics.mean.remote(values)
    elif request.operation == "correlation":
        result = await analytics.correlation.remote(values)
    elif request.operation == "matrix_multiply":
        result = await analytics.matrix_multiply.remote(values)
    else:  # pca
        result = await analytics.pca.remote(values)
    
    computation_time = asyncio.get_event_loop().time() - start_time
    
    return AnalyticsResponse(
        result=result,
        computation_time=computation_time,
        used_gpu=request.gpu_enabled,
        operation=request.operation
    )

@app.post(
    "/recipes",
    response_model=Dict[str, Any],
    tags=["recipes"]
)
async def create_recipe(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new recipe."""
    return recipe

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 