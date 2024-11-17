# src/app.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pathlib import Path
from .rag.lmstudio_client import LMStudioClient
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Initialize LM Studio client
client = LMStudioClient()

class Query(BaseModel):
    question: str
    context: Optional[str] = None

def create_template():
    """Create the HTML template"""
    template_content = """<!DOCTYPE html>
    <html>
    <head>
        <title>Uganda Clinical Guidelines Chatbot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .chat-container {
                background-color: white;
                border: 1px solid #ddd;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-top: 20px;
            }
            .input-container {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }
            input[type="text"] {
                flex-grow: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }
            button {
                padding: 12px 24px;
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                transition: background-color 0.2s;
            }
            button:hover {
                background-color: #0056b3;
            }
            .response {
                margin-top: 20px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 4px;
                border-left: 4px solid #007bff;
            }
            #error {
                color: #dc3545;
                margin-top: 10px;
                padding: 10px;
                border-radius: 4px;
                display: none;
            }
            .loading {
                display: none;
                margin: 20px 0;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <h1>Uganda Clinical Guidelines Chatbot</h1>
        <p>Ask questions about the Uganda Clinical Guidelines 2023</p>
        
        <div class="chat-container">
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
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question })
                    });
                    
                    const data = await response.json();
                    loadingDiv.style.display = 'none';
                    
                    if (response.ok) {
                        responseDiv.innerHTML = `
                            <strong>Question:</strong><br>
                            ${question}<br><br>
                            <strong>Answer:</strong><br>
                            ${data.response}<br><br>
                            <em>Model: ${data.metadata.model}</em>
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
    if client.test_connection():
        return {"status": "healthy", "model": client.model_name}
    raise HTTPException(status_code=503, detail="LM Studio not available")

@app.post("/chat")
async def chat(query: Query) -> Dict[str, Any]:
    """Chat endpoint"""
    try:
        response = client.query(query.question, query.context)
        return response
    except Exception as e:
        logger.error(f"Chat failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))