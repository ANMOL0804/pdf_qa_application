import React, { useState, useRef } from "react";
import "./index.css";

const API_BASE_URL  = "http://127.0.0.1:8000";

function App() {
  const [file, setFile] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [summary, setSummary] = useState("");
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  async function uploadFile(event) {
    event.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_BASE_URL}/pdf/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Failed to upload PDF.");
      }

      setSessionId(data.session_id);
      setSummary(data.summary);
      setMessages([{ text: "Summary: " + data.summary, sender: "bot" }]);
      setError(null);
    } catch (err) {
      setError(err.message);
      alert(err.message);
      window.location.reload();
    }
  }

  async function sendMessage(event) {
    event.preventDefault();
    if (!input || !sessionId) return;

    const response = await fetch(`${API_BASE_URL}/pdf/chat/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: input,
      }),
    });

    const data = await response.json();
    setMessages((prev) => [
      ...prev,
      { text: input, sender: "user" },
      { text: data.response, sender: "bot" },
    ]);
    setInput("");
  }

  async function endChat() {
    if (!sessionId) return;

    try {
      await fetch(`${API_BASE_URL}/pdf/chat/end/${sessionId}`, {
        method: "DELETE",
      });
      // Reset state
      setSessionId(null);
      setSummary("");
      setMessages([]);
      setFile(null);
      setError(null);
    } catch (error) {
      console.error("Error ending chat:", error);
    }
  }

  // Drag & drop file handling
  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    validateFile(droppedFile);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleUploadAreaClick = () => {
    fileInputRef.current.click();
  };

  const validateFile = (selectedFile) => {
    if (selectedFile && selectedFile.type !== "application/pdf") {
      alert("Please upload a valid PDF file.");
      window.location.reload();
    } else {
      setFile(selectedFile);
    }
  };

  return (
    <div className="app-container">
      <h1>PDF Q&A Chatbot</h1>
      {error && <div className="error-box">❌ {error}</div>}
      {!sessionId && (
        <form onSubmit={uploadFile}>
          <div
            className="upload-area"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={handleUploadAreaClick}
          >
            {file ? (
              <p>Selected file: {file.name}</p>
            ) : (
              <p>Drag & drop your PDF here, or click to select a file</p>
            )}
          </div>
          <input
            type="file"
            ref={fileInputRef}
            style={{ display: "none" }}
            onChange={(e) => validateFile(e.target.files[0])}
          />
          <button type="submit" className="upload-btn">Upload PDF</button>
        </form>
      )}

      {summary && <div className="summary-box">📄 {summary}</div>}

      {sessionId && (
        <div className="chat-container">
          <div className="messages-box">
            {messages.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.sender}`}>
                {msg.text}
              </div>
            ))}
          </div>
          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              className="chat-input"
            />
            <button type="submit" className="send-btn">Send</button>
          </form>
          <button className="end-chat-btn" onClick={endChat}>
            End Chat
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
