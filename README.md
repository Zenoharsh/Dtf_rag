# DTF-AI: A RAG-Powered Chatbot for the Dattopant Thengadi Foundation

![Image](https://github.com/user-attachments/assets/ad4b1390-ee56-499c-94ac-b69bd681b64d)

This repository contains the full-stack implementation of an AI-powered chatbot for the [Dattopant Thengadi Foundation website](https://dtforg.in). The chatbot uses a Retrieval-Augmented Generation (RAG) pipeline to answer user questions based on a private collection of documents, including PDFs and scraped website content.

**Live Demo:** [dtforg.in](https://dtforg.in)

Please click on the Chatbot icon in the right-bottom corner to ask relevant queries.

## Features

- **RAG Pipeline:** Answers questions using context from private documents, reducing hallucinations.
- **Self-Hosted LLM:** Runs a local `gemma2:2b` model using **Ollama** for data privacy and control.
- **Streaming Responses:** Provides a real-time "typewriter" effect for a better user experience.
- **Secure Backend:** Built with **FastAPI** and deployed behind an **NGINX** reverse proxy with SSL.
- **Robust Deployment:** Managed by **PM2** for continuous uptime and automated restarts.
- **Custom Frontend:** A clean, interactive chat widget built with vanilla JavaScript, HTML, and CSS.

---

## Tech Stack

- **Backend:** Python, FastAPI, LlamaIndex, Ollama
- **Frontend:** HTML, CSS, JavaScript, Marked.js
- **Deployment:** Ubuntu VPS, NGINX, PM2, Cron, UFW Firewall, Certbot (SSL)
- **AI Model:** `gemma2:2b`
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`

---

## Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/Zenoharsh/Dtf_rag.git](https://github.com/Zenoharsh/Dtf_rag.git)
    cd dtf-ai
    ```

2.  **Install backend dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Ollama:**

    - Install Ollama from [ollama.com](https://ollama.com).
    - Pull the required model:
      ```bash
      ollama pull gemma2:2b
      ```

4.  **Add your documents:**

    - Place your PDF and `.txt` files inside the `data/` directory.

5.  **Run the backend server:**
    ```bash
    python main.py
    ```
    The server will be available at `http://localhost:8000`.

---

## Project Structure
```bash
/dtf-ai
├── data/ # Source documents (PDFs, TXT files)
├── public/ # (Optional) For frontend assets like widget.js
├── storage/ # Auto-generated vector index
├── main.py # The FastAPI backend application
├── keep_alive.sh # Cron script to prevent model cold starts
├── requirements.txt # Python dependencies
└── README.md # This file
```
---

## Future Improvements

- [ ] Implement a more robust data pre-processing pipeline.
- [ ] Add a "Stop Generating" button to the frontend.
- [ ] Integrate a database for logging user queries and feedback.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
