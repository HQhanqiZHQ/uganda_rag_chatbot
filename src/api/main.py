# src/api/main.py
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, validator
from typing import Optional, Dict, Any
from pathlib import Path
import time
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..config import settings
from ..logger import setup_logger
from ..rag.llm_client import LLMClient

logger = setup_logger("api")

# Initialize LM clients
lm_studio_client = LLMClient(
    model_type="lmstudio",
    model_name="llama-3.2-3b-instruct",
    api_key=settings.OPENAI_API_KEY  # Make sure to pass the API key
)

# Only initialize OpenAI client if API key is valid
openai_client = None
if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_key_here":
    openai_client = LLMClient(
        model_type="openai",
        model_name="gpt-4",
        api_key=settings.OPENAI_API_KEY
    )

# Set up FastAPI app
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Uganda Clinical Guidelines Chatbot")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Set up static files and templates
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class Query(BaseModel):
    question: str
    model: str = "lmstudio"
    temperature: Optional[float] = 0.3
    
    @validator('question')
    def validate_question(cls, v):
        if len(v.strip()) < 10:
            raise ValueError('Question too short (minimum 10 characters)')
        if len(v) > 500:
            raise ValueError('Question too long (maximum 500 characters)')
        return v.strip()
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Temperature must be between 0 and 1')
        return v

def create_template():
    """Create the HTML template with model selection"""
    template_path = TEMPLATES_DIR / "index.html"
    if template_path.exists():
        return
        
    template_content = """<!DOCTYPE html>
    <html>
    <head>
        <title>Uganda Clinical Guidelines Chatbot</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px;
                background-color: #f5f5f5;
            }
            .chat-container { 
                max-width: 800px; 
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .input-container { 
                margin: 20px 0;
                display: flex;
                gap: 10px;
            }
            input[type="text"] { 
                flex-grow: 1;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button { 
                padding: 10px 20px;
                background: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            button:hover {
                background: #0056b3;
            }
            .response { 
                margin-top: 20px; 
                white-space: pre-wrap;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
            }
            .loading { 
                display: none;
                color: #666;
                margin: 10px 0;
            }
            #error { 
                color: #dc3545;
                display: none;
                margin: 10px 0;
                padding: 10px;
                border-radius: 4px;
                background: #f8d7da;
            }
            .model-select { 
                margin-bottom: 20px;
                display: flex;
                gap: 10px;
                align-items: center;
            }
            select, input[type="number"] { 
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <h1>Uganda Clinical Guidelines Chatbot</h1>
            
            <div class="model-select">
                <select id="model">
                    <option value="lmstudio">LM Studio (Local)</option>
                    <option value="openai">OpenAI GPT-4</option>
                </select>
                <label for="temperature">Temperature:</label>
                <input type="number" id="temperature" value="0.3" min="0" max="1" step="0.1">
            </div>
            
            <div class="input-container">
                <input type="text" id="question" placeholder="Enter your medical question (minimum 10 characters)...">
                <button onclick="sendQuestion()">Ask</button>
            </div>
            <div id="error"></div>
            <div id="loading" class="loading">Processing your question...</div>
            <div id="response" class="response"></div>
        </div>

# Continue in templates/index.html script section:
        <script>
            async function sendQuestion() {
                const questionInput = document.getElementById('question');
                const modelSelect = document.getElementById('model');
                const temperatureInput = document.getElementById('temperature');
                const responseDiv = document.getElementById('response');
                const errorDiv = document.getElementById('error');
                const loadingDiv = document.getElementById('loading');
                
                const question = questionInput.value.trim();
                if (!question) {
                    errorDiv.textContent = 'Please enter a question';
                    errorDiv.style.display = 'block';
                    return;
                }
                
                errorDiv.style.display = 'none';
                loadingDiv.style.display = 'block';
                responseDiv.innerHTML = '';
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            question: question,
                            model: modelSelect.value,
                            temperature: parseFloat(temperatureInput.value)
                        })
                    });
                    
                    const data = await response.json();
                    loadingDiv.style.display = 'none';
                    
                    if (response.ok) {
                        responseDiv.innerHTML = `
                            <strong>Question:</strong> ${question}\n\n
                            <strong>Answer:</strong> ${data.response}\n\n
                            <em>Model: ${data.metadata.model}, Temperature: ${data.metadata.temperature}</em>`;
                        questionInput.value = '';
                    } else {
                        errorDiv.textContent = data.detail || 'Error occurred';
                        errorDiv.style.display = 'block';
                    }
                } catch (error) {
                    loadingDiv.style.display = 'none';
                    errorDiv.textContent = 'Failed to get response';
                    errorDiv.style.display = 'block';
                    console.error('Error:', error);
                }
            }
            
            document.getElementById('question').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') sendQuestion();
            });
        </script>
    </body>
    </html>"""
    
    with open(template_path, "w") as f:
        f.write(template_content)
    logger.info(f"Created template at {template_path}")

# Create template on startup
create_template()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models": {
            "lmstudio": "available",
            "openai": "available" if openai_client else "not configured"
        }
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
@limiter.limit("5/minute")
async def chat(query: Query, request: Request) -> Dict[str, Any]:
    """Handle chat requests with rate limiting"""
    try:
        start_time = time.time()
        
        # Select appropriate client
        if query.model == "openai":
            if not openai_client:
                raise HTTPException(
                    status_code=400,
                    detail="OpenAI API key not configured"
                )
            client = openai_client
        else:
            client = lm_studio_client
        
        # Get response
        response = client.query(
            question=query.question,
            temperature=query.temperature
        )
        
        # Add latency to metadata
        response['metadata']['latency'] = round(time.time() - start_time, 2)
        
        logger.info(
            f"Chat response generated",
            extra={
                "model": query.model,
                "temperature": query.temperature,
                "latency": response['metadata']['latency']
            }
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

                