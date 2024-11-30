```git clone <your-repo>```

```conda env create -f environment.yml```

```conda activate uganda-rag```

The LM Studio(Local) model is llama-3.2-3b-instruct.
The GPT model is GPT-4 (create a .env file in the root folder of the git repo, put your OPENAI_API_KEY=XXXX there)

Open LM Studio, load the llama-3.2-3b-instruct model, then go to the git repo, 
run
```python main.py```.

go to your browser ```http://localhost:8000/```
<img width="731" alt="v2_screenshot1" src="https://github.com/user-attachments/assets/bdc37edb-f1f2-4fde-9acb-8e17d13d5bcb">

<img width="665" alt="v2_screenshot2" src="https://github.com/user-attachments/assets/07f7083d-8641-41e4-be90-bdc8f437627b">




-------------------
Make sure your dockerdesktop is open.
```docker run -p 8080:8000 -v $(pwd)/chroma_data:/chroma/chroma chromadb/chroma```
