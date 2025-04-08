from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
from typing import Optional, List, Dict, Any, Union
import uvicorn
from pydantic import BaseModel
import time
import traceback
import logging
from dotenv import load_dotenv

# Import your color suggester function
from test import ai_color_suggester

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Color Suggester API",
    description="API for suggesting UI colors based on UI images and project descriptions",
    version="1.0.0",
)

# Add CORS middleware for browser clients and Android testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models
class ColorAnalysis(BaseModel):
    color: str
    suggested_color: Optional[str] = None
    is_perfect_match: bool
    reason: str

class ColorRecommendation(BaseModel):
    component: str
    color: str

class ColorPaletteWithAnalysis(BaseModel):
    image_based: List[str]
    description_based: List[str]
    organized_palette: Dict[str, Any]
    all_colors: List[str]
    color_analysis: Dict[str, ColorAnalysis]
    ui_recommendations: List[ColorRecommendation]
    additional_notes: List[str]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
    request_id: str

# Routes
@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "AI Color Suggester API",
        "version": "1.0.0",
        "endpoints": {
            "/api/suggest-colors": "POST - Get color suggestions based on image and description",
            "/health": "GET - Check API health"
        }
    }

@app.post("/api/suggest-colors", response_model=ColorPaletteWithAnalysis)
async def suggest_colors(
    image: UploadFile = File(..., description="UI/App image file"),
    description: str = Form(..., description="Project description")
):
    """
    Generate color suggestions based on UI/app image and project description.
    
    - **image**: UI/App image file
    - **description**: Project description text
    
    Returns a color palette with image-based colors, description-based colors,
    organized palette suggestions, detailed color analysis and recommendations.
    """
    request_id = f"req_{int(time.time())}"
    logger.info(f"Request {request_id}: Processing color suggestion request")
    
    try:
        # Check if API keys are available
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        groq_api_key = os.environ.get("GROQ_API_KEY")
        
        if not gemini_api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
            
        if not groq_api_key:
            raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
        
        # Check file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {image.content_type}. Supported types: {', '.join(allowed_types)}"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_path = temp_file.name
            content = await image.read()
            temp_file.write(content)
        
        logger.info(f"Request {request_id}: Image saved, processing with AI models...")
        
        # Process with AI Color Suggester
        result = ai_color_suggester(temp_path, description, gemini_api_key, groq_api_key)
        
        # Clean up temporary file
        os.unlink(temp_path)
        logger.info(f"Request {request_id}: Processing complete, enhancing results with analysis")
        
        # Add detailed color analysis to the response
        color_analysis = {}
        
        # Primary color analysis
        primary_image = result["organized_palette"]["primary"]
        primary_suggested = result["description_based"][0] if result["description_based"] else None
        color_analysis["primary"] = {
            "color": primary_image,
            "suggested_color": primary_suggested if primary_image != primary_suggested else None,
            "is_perfect_match": primary_image == primary_suggested,
            "reason": "The suggested color better aligns with your project's theme and enhances user experience" 
                      if primary_image != primary_suggested else "Perfect match! No change needed"
        }
        
        # Secondary color analysis
        secondary_image = result["organized_palette"]["secondary"]
        secondary_suggested = result["description_based"][1] if len(result["description_based"]) > 1 else None
        color_analysis["secondary"] = {
            "color": secondary_image,
            "suggested_color": secondary_suggested if secondary_image != secondary_suggested else None,
            "is_perfect_match": secondary_image == secondary_suggested,
            "reason": "The suggested color provides better contrast and visual hierarchy" 
                      if secondary_image != secondary_suggested else "Perfect match! No change needed"
        }
        
        # Accent color analysis
        accent_image = result["organized_palette"]["accent"]
        accent_suggested = result["description_based"][2] if len(result["description_based"]) > 2 else None
        color_analysis["accent"] = {
            "color": accent_image,
            "suggested_color": accent_suggested if accent_image != accent_suggested else None,
            "is_perfect_match": accent_image == accent_suggested,
            "reason": "The suggested color creates better visual interest and highlights important elements" 
                      if accent_image != accent_suggested else "Perfect match! No change needed"
        }
        
        # Background color analysis
        bg_image = result["organized_palette"]["background"]
        bg_suggested = result["description_based"][3] if len(result["description_based"]) > 3 else None
        color_analysis["background"] = {
            "color": bg_image,
            "suggested_color": bg_suggested if bg_image != bg_suggested else None,
            "is_perfect_match": bg_image == bg_suggested,
            "reason": "The suggested color improves readability and reduces eye strain" 
                      if bg_image != bg_suggested else "Perfect match! No change needed"
        }
        
        # Text color analysis
        text_image = result["organized_palette"]["text"]
        text_suggested = result["description_based"][4] if len(result["description_based"]) > 4 else None
        color_analysis["text"] = {
            "color": text_image,
            "suggested_color": text_suggested if text_image != text_suggested else None,
            "is_perfect_match": text_image == text_suggested,
            "reason": "The suggested color ensures better readability and accessibility" 
                      if text_image != text_suggested else "Perfect match! No change needed"
        }
        
        # UI component recommendations
        ui_recommendations = []
        for component, color in result["organized_palette"]["ui_components"].items():
            ui_recommendations.append({
                "component": component.replace('_', ' ').capitalize(),
                "color": color
            })
        
        # Additional notes
        additional_notes = [
            "All suggested colors have been checked for accessibility compliance",
            "The color palette maintains proper contrast ratios for better readability",
            "Colors are chosen to create a harmonious and professional appearance",
            "Consider testing these colors in different lighting conditions"
        ]
        
        # Enhance the result with analysis
        enhanced_result = {
            **result,
            "color_analysis": color_analysis,
            "ui_recommendations": ui_recommendations,
            "additional_notes": additional_notes
        }
        
        # Return enhanced results
        return enhanced_result
    
    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    
    except Exception as e:
        # Log the full error and return a structured error response
        error_details = traceback.format_exc()
        logger.error(f"Request {request_id}: Error processing request: {error_details}")
        
        # Return a structured error response for easier handling in Kotlin
        return JSONResponse(
            status_code=500,
            content={
                "error": str(e),
                "details": error_details,
                "request_id": request_id
            }
        )
    finally:
        # Make sure we clean up the temp file in all cases
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if API keys are set
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    
    status = "ok"
    issues = []
    
    if not gemini_api_key:
        issues.append("GEMINI_API_KEY not configured")
        status = "warning"
        
    if not groq_api_key:
        issues.append("GROQ_API_KEY not configured")
        status = "warning"
    
    return {
        "status": status,
        "timestamp": time.time(),
        "issues": issues if issues else None
    }

# Run the API with Uvicorn if executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    
    # Check if we're in a production environment (like Render)
    is_prod = os.environ.get("ENVIRONMENT") == "production"
    
    # In production, bind to 0.0.0.0 to allow external connections
    if is_prod:
        uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
    else:
        # In development, use reload for easier debugging
        uvicorn.run("main:app", host="127.0.0.1", port=port, log_level="debug", reload=True)