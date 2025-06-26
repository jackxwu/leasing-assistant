import React, { useState, useEffect } from 'react';
import { chatApi, ConversationHistory as ConversationHistoryType } from '../services/chatApi';
import './ConversationHistory.css';

interface ConversationHistoryProps {
  onClose: () => void;
}

const ConversationHistory: React.FC<ConversationHistoryProps> = ({ onClose }) => {
  const [history, setHistory] = useState<ConversationHistoryType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadHistory = async () => {
      try {
        setLoading(true);
        const conversationHistory = await chatApi.getConversationHistory();
        setHistory(conversationHistory);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load conversation history');
      } finally {
        setLoading(false);
      }
    };

    loadHistory();
  }, []);

  if (loading) {
    return (
      <div className="conversation-history-overlay">
        <div className="conversation-history-modal">
          <div className="conversation-history-header">
            <h2>Conversation History</h2>
            <button onClick={onClose} className="close-button">×</button>
          </div>
          <div className="conversation-history-content">
            <div className="loading">Loading conversation history...</div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="conversation-history-overlay">
        <div className="conversation-history-modal">
          <div className="conversation-history-header">
            <h2>Conversation History</h2>
            <button onClick={onClose} className="close-button">×</button>
          </div>
          <div className="conversation-history-content">
            <div className="error">Error: {error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="conversation-history-overlay">
      <div className="conversation-history-modal">
        <div className="conversation-history-header">
          <h2>Conversation History</h2>
          <button onClick={onClose} className="close-button">×</button>
        </div>
        <div className="conversation-history-content">
          {!history || history.messages.length === 0 ? (
            <div className="no-history">No conversation history found.</div>
          ) : (
            <div className="messages-list">
              {history.messages.map((message, index) => (
                <div
                  key={index}
                  className={`message ${message.role === 'user' ? 'user-message' : 'agent-message'}`}
                >
                  <div className="message-header">
                    <span className="sender">
                      {message.role === 'user' ? 'You' : 'Assistant'}
                    </span>
                  </div>
                  <div className="message-content">
                    {message.content}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConversationHistory;