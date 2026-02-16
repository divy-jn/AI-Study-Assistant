# AI Study Assistant - Full Project Development Log
> **Generated on:** 2026-02-16
> **Current Version:** 2.0 (Enhanced Chat Platform)

## 1. Project Overview & Vision

The **"Mini"** project is an advanced AI-powered study assistant built to bridge the gap between static study materials and interactive learning.

**Core Mission:** To create a personalized learning companion that doesn't just "chat," but understands a student's *actual* study material (notes, PDFs, textbooks) and helps clarify doubts, solve problems, and structure their learning path.

---

## 2. Development Journey

The project was developed in two distinct phases:

### Phase 1: The MVP (Initial Foundation)
We started with a minimalistic prototype to validate the core RAG (Retrieval-Augmented Generation) pipeline.
*   **Backend**: Basic FastAPI structure (`app/`), SQLite database for users/auth using JWT.
*   **AI Engine**: Integrated `Ollama` for running local LLMs (like Qwen/Llama) and `ChromaDB` for vector search.
*   **Document Processing**: A basic `document_processor` that could ingest PDFs and split them into chunks.
*   **Frontend**: A simple HTML page (`index.html`) with a single text box. It could send a query and get a stream of text back. No history, no formatting, no uploads.

### Phase 2: The "Version 2.0" Overhaul (Current State)
We then transformed this MVP into a full-fledged production-grade application. This involved rewriting almost 100% of the frontend code and significantly hardening the backend.
*   **Goal**: To make the interface as polished and usable as modern tools like ChatGPT or Gemini.
*   **Key Upgrades**: Added persistent chat history, math rendering, file uploads, smart suggestions, and robust error handling.

---

## 3. Technical Architecture & Codebase

### A. Backend (`app/`)
Built with **Python** and **FastAPI** for high-performance asynchronous handling.

| File / Module | Responsibility |
| :--- | :--- |
| **`main.py`** | Entry point. Configures the app, CORS, static files, and database connection. |
| **`api/auth.py`** | Handles User Registration & Login. Uses `bcrypt` for password hashing and `PyJWT` for secure session tokens. |
| **`api/chat.py`** | The brain of the chat. Manages real-time streaming (Server-Sent Events), conversation state, and calls the LLM service. |
| **`api/documents.py`** | Manages file uploads. Validates file types (PDF/TXT), saves them to `data/uploads/`, and triggers the embedding process. |
| **`services/llm_service.py`** | Abstraction layer for `Ollama`. Handles prompt construction, context management, and streaming response generation. |
| **`services/document_processor.py`** | The "ETL" pipeline. Reads files -> Cleans text -> Splits into smart chunks -> Generates embeddings -> Stores in ChromaDB. |

### B. Frontend (`static/`)
A single-page application (SPA) built with **Vanilla JavaScript**, **HTML5**, and custom **CSS**. No heavy frameworks (React/Vue) were used to keep it lightweight and fast.

| Component | Responsibility |
| :--- | :--- |
| **`index.html`** | Contains the entire UI layout (Sidebar + Chat Area). |
| **Sidebar Logic** | Manages the list of conversations. Handles creating new chats, renaming, deleting, and switching context. |
| **Chat Logic** | Handles message rendering, markdown parsing (bold/code), and the real-time "typing" effect. |
| **Math Engine** | Integrated **KaTeX** to render complex LaTeX formulas (e.g., `$\int_{0}^{\infty} x^2 dx$`) beautifully. |

---

## 4. Comprehensive Feature List (Version 2.0)

### 💬 Advanced Chat Interface
*   **Sidebar History**: Complete history of past conversations, auto-saved to the database.
*   **Auto-Titles**: The AI automatically generating a short, descriptive title for new generic chats (e.g., "Physics Doubt" instead of "New Chat").
*   **Message Actions**: Hover over any message to **Copy** it or **Edit** your own questions to re-generate an answer.
*   **Smart Scrolling**: Keeps the view stable while reading previous messages, even if the AI is still generating new text.
*   **Follow-up Chips**: The AI proactively suggests 3 relevant follow-up questions after every answer to keep the learning flowing.

### 📚 Document Integration
*   **One-Click Upload**: A paperclip icon allow users to upload PDF notes directly from the chat bar.
*   **RAG Pipeline**: The system automatically indexes these uploads so the AI generally "knows" what's in your notes when answering questions.

### 🧮 Academic-Ready
*   **Math Support**: Full support for scientific notation and advanced math formulas via LaTeX/KaTeX.
*   **Code Blocks**: Syntax highlighting for coding questions.

---

## 5. Challenges & Solutions (Development Log)

Building this required overcoming several technical hurdles:

### 🔴 Challenge 1: Rendering Math Properly
**The Issue:** The AI outputs raw LaTeX code (`$$x^2$$`), which looks like garbage text to users.
**The Fix:** We integrated **KaTeX** and wrote a custom parser in `index.html` to detect `$` delimiters and convert them into HTML math elements on the fly.

### 🔴 Challenge 2: Handling Large File Uploads
**The Issue:** Uploading documents failed with obscure "Server Error 500" messages.
**Root Cause:**
1.  **Type Error:** The code tried to access `user.id` on a dictionary object (needed `user["id"]`).
2.  **Method Mismatch:** The API called `process_document()` but the service method was named `process_file()`.
**The Fix:** We debugged standard logs, corrected the dictionary access, fixed the method call, and removed an incorrect `await` (since the function was synchronous).

### 🔴 Challenge 3: Streaming Stability
**The Issue:** The chat window would violently jump to the bottom with every new character printed, making it impossible to read older messages.
**The Fix:** Implemented "Smart Scroll" logic in JS. The window now only auto-scrolls if the user is *already* at the bottom. If they scroll up to read, we respect that position.

### 🔴 Challenge 4: Preventing Duplicate Logic
**The Issue:** During rapid iteration, the `index.html` file accidentally duplicated its entire script block, doubling the file size and causing weird bugs (double-sending messages).
**The Fix:** We performed a manual code audit, identified the redundant 500+ lines of code, and cleanly removed them.

---

## 6. Future Roadmap

The project has a solid foundation. Next steps for Version 3.0:
1.  **Voice Interaction**: Add Speech-to-Text for a conversational "tutor" mode.
2.  **Visual Input**: Allow users to snap photos of handwritten notes/formulas for parsing.
3.  **Cloud Sync**: Move from local SQLite to a cloud DB (PostgreSQL) for multi-device access.

---

## 7. Change Log & Updates

### Update: 2026-02-16 (Documentation Refactor)
- **Action**: Created dedicated `text_documentation/` folder.
- **Reason**: To keep the project root clean and organize all non-code deliverables.
- **Moved Files**: `PROJECT_REPORT.md` and `RESEARCH_REPORT.md` are now located in `text_documentation/`.

