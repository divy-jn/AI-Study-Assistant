# AI Educational Document Reasoning System - Project Structure

```
ai-edu-system/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI main application
│   │   ├── config.py                    # Configuration settings
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                  # Authentication endpoints
│   │   │   ├── documents.py             # Document upload/management
│   │   │   ├── chat.py                  # Chat/query endpoints
│   │   │   └── generation.py            # Question/exam generation
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py                  # User database models
│   │   │   ├── document.py              # Document metadata models
│   │   │   └── conversation.py          # Chat history models
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py          # Authentication logic
│   │   │   ├── document_processor.py    # Document parsing & chunking
│   │   │   ├── embedding_service.py     # Vector embedding generation
│   │   │   ├── vector_store.py          # ChromaDB operations
│   │   │   └── llm_service.py           # Ollama LLM interface
│   │   │
│   │   ├── langgraph_workflow/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py                 # Main LangGraph definition
│   │   │   ├── state.py                 # State schema
│   │   │   ├── nodes/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── intent_classifier.py # Intent identification
│   │   │   │   ├── document_retriever.py# Document retrieval
│   │   │   │   ├── answer_generator.py  # Answer generation
│   │   │   │   ├── answer_evaluator.py  # Answer evaluation
│   │   │   │   ├── doubt_resolver.py    # Doubt clarification
│   │   │   │   ├── question_generator.py# Question generation
│   │   │   │   └── exam_generator.py    # Exam paper generation
│   │   │   └── routers/
│   │   │       ├── __init__.py
│   │   │       └── intent_router.py     # Routing logic
│   │   │
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── sqlite_db.py             # SQLite connection
│   │   │   └── schemas.sql              # Database schema
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── text_processing.py       # Text utilities
│   │       ├── pdf_parser.py            # PDF extraction
│   │       ├── docx_parser.py           # DOCX extraction
│   │       └── prompts.py               # LLM prompt templates
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_document_processing.py
│   │   ├── test_langgraph.py
│   │   └── test_api.py
│   │
│   ├── data/
│   │   ├── uploads/                     # User uploaded documents
│   │   ├── chroma_db/                   # ChromaDB persistence
│   │   └── sqlite.db                    # SQLite database file
│   │
│   ├── requirements.txt                 # Python dependencies
│   ├── .env.example                     # Environment variables template
│   └── README.md
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Auth/
│   │   │   │   ├── Login.jsx
│   │   │   │   └── Register.jsx
│   │   │   ├── Dashboard/
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   └── DocumentList.jsx
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.jsx
│   │   │   │   ├── MessageBubble.jsx
│   │   │   │   └── InputBox.jsx
│   │   │   ├── Documents/
│   │   │   │   ├── UploadDocument.jsx
│   │   │   │   └── DocumentViewer.jsx
│   │   │   └── Generation/
│   │   │       ├── QuestionGenerator.jsx
│   │   │       └── ExamPaperGenerator.jsx
│   │   ├── services/
│   │   │   ├── api.js                   # Axios API configuration
│   │   │   └── auth.js                  # Auth service
│   │   ├── context/
│   │   │   └── AuthContext.jsx          # Auth state management
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── scripts/
│   ├── setup_ollama.bat                 # Windows Ollama setup
│   ├── install_dependencies.bat         # Install Python packages
│   └── start_dev.bat                    # Start development servers
│
└── docs/
    ├── API_DOCUMENTATION.md
    ├── SETUP_GUIDE.md
    └── USER_GUIDE.md
```

## File Count Summary:
- Backend Python files: ~35 files
- Frontend React files: ~20 files
- Configuration files: ~8 files
- Documentation: ~5 files

**Total: ~68 files**
