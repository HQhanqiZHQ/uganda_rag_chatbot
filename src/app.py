# src/app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pathlib import Path
from src.rag.llm_client import LLMClient
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize LLM clients
lm_studio_client = LLMClient(
    model_type="lmstudio",
    model_name="llama-3.2-3b-instruct"
)

openai_client = LLMClient(
    model_type="openai",
    model_name="gpt-4",  # or "gpt-3.5-turbo"
    api_key=os.getenv("OPENAI_API_KEY")
) if os.getenv("OPENAI_API_KEY") else None

# Set up paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="Uganda Clinical Guidelines Chatbot")

# Setup templates and static files
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class Query(BaseModel):
    question: str
    context: Optional[str] = None
    model: str = "lmstudio"  # "lmstudio" or "openai"
    temperature: Optional[float] = 0.3

def create_template():
    """Create the HTML template with model selection"""
    template_content = """<!DOCTYPE html>
    <html>
    <head>
        <title>Uganda Clinical Guidelines Chatbot</title>
        <style>
            /* ... (previous styles) ... */
            .model-select {
                margin-bottom: 20px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
            .model-select select {
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
            .temperature-control {
                margin-left: 20px;
                display: inline-block;
            }
            .temperature-control input {
                width: 60px;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
        </style>
    </head>
    <body>
        <h1>Uganda Clinical Guidelines Chatbot</h1>
        <p>Ask questions about the Uganda Clinical Guidelines 2023</p>
        
        <div class="chat-container">
            <div class="model-select">
                <label for="model">Select Model:</label>
                <select id="model">
                    <option value="lmstudio">LM Studio (Local)</option>
                    <option value="openai">OpenAI GPT-4</option>
                </select>
                
                <span class="temperature-control">
                    <label for="temperature">Temperature:</label>
                    <input type="number" id="temperature" value="0.3" min="0" max="1" step="0.1">
                </span>
            </div>
            
            <div class="input-container">
                <input type="text" id="question" placeholder="Enter your medical question...">
                <button onclick="sendQuestion()">Ask</button>
            </div>
            <div id="error"></div>
            <div id="loading" class="loading">Processing your question...</div>
            <div id="response" class="response"></div>
        </div>

        <script>
            async function sendQuestion() {
                const questionInput = document.getElementById('question');
                const modelSelect = document.getElementById('model');
                const temperatureInput = document.getElementById('temperature');
                const responseDiv = document.getElementById('response');
                const errorDiv = document.getElementById('error');
                const loadingDiv = document.getElementById('loading');
                
                const question = questionInput.value.trim();
                const model = modelSelect.value;
                const temperature = parseFloat(temperatureInput.value);
                
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
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            question: question,
                            model: model,
                            temperature: temperature
                        })
                    });
                    
                    const data = await response.json();
                    loadingDiv.style.display = 'none';
                    
                    if (response.ok) {
                        responseDiv.innerHTML = `
                            <strong>Question:</strong><br>
                            ${question}<br><br>
                            <strong>Answer:</strong><br>
                            ${data.response}<br><br>
                            <em>Model: ${data.metadata.model} (${data.metadata.type})</em>
                        `;
                        questionInput.value = '';
                    } else {
                        errorDiv.textContent = data.detail || 'An error occurred';
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
                if (e.key === 'Enter') {
                    sendQuestion();
                }
            });
        </script>
    </body>
    </html>"""
    
    template_path = TEMPLATES_DIR / "index.html"
    with open(template_path, "w") as f:
        f.write(template_content)
    logger.info(f"Created template at {template_path}")

# Create template on import
create_template()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "lmstudio": lm_studio_client.test_connection(),
        "openai": openai_client.test_connection() if openai_client else False
    }
    return {"status": status}

@app.post("/chat")
async def chat(query: Query) -> Dict[str, Any]:
    """Chat endpoint"""
    try:
        if query.model == "openai" and not openai_client:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured"
            )
        
        client = openai_client if query.model == "openai" else lm_studio_client
        return client.query(
            question=query.question,
            context=query.context,
            temperature=query.temperature
        )
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))