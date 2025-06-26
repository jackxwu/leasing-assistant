import React, { useState, useEffect, useRef } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ActionButton } from './ActionButton';
import ConversationHistory from './ConversationHistory';
import { chatApi } from '../services/chatApi';
import { ChatMessage as ChatMessageType, ChatResponse, Lead, Preferences } from '../types/chat';
import './ChatWorkspace.css';

interface ChatWorkspaceProps {
  lead: Lead;
  preferences?: Preferences;
  communityId: string;
}

export const ChatWorkspace: React.FC<ChatWorkspaceProps> = ({
  lead,
  preferences,
  communityId
}) => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [lastResponse, setLastResponse] = useState<ChatResponse | null>(null);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (text: string, sender: 'user' | 'agent') => {
    const newMessage: ChatMessageType = {
      id: Date.now().toString(),
      text,
      sender,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newMessage]);
  };

  const handleSendMessage = async (messageText: string) => {
    setIsLoading(true);
    addMessage(messageText, 'user');

    try {
      const response = await chatApi.sendMessage({
        lead,
        message: messageText,
        preferences,
        community_id: communityId
      });

      addMessage(response.reply, 'agent');
      setLastResponse(response);
    } catch (error) {
      console.error('Error sending message:', error);
      addMessage('Sorry, there was an error processing your message. Please try again.', 'agent');
    } finally {
      setIsLoading(false);
    }
  };

  const handleActionClick = (action: string, data?: any) => {
    switch (action) {
      case 'confirm_tour':
        addMessage(`Great! I've confirmed your tour for ${new Date(data.time).toLocaleString()}. You'll receive a confirmation email shortly.`, 'agent');
        setLastResponse(null);
        break;
      case 'connect_human':
        addMessage('Connecting you with a human agent now. Please hold on...', 'agent');
        setLastResponse(null);
        break;
    }
  };

  return (
    <div className="chat-workspace">
      <div className="chat-header">
        <h2>Chat with {communityId === 'unknown' ? 'Leasing Assistant' : communityId.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}</h2>
        <div className="header-actions">
          <button 
            className="history-button"
            onClick={() => setShowHistory(true)}
            title="View conversation history"
          >
            📖 History
          </button>
          <div className="lead-info">
            <span>{lead.name} ({lead.email})</span>
          </div>
        </div>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <p>Hello {lead.name}! How can I help you today?</p>
          </div>
        )}
        
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="loading-indicator">
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}
        
        {lastResponse && (
          <ActionButton 
            response={lastResponse} 
            onActionClick={handleActionClick}
          />
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <ChatInput 
        onSendMessage={handleSendMessage}
        disabled={isLoading}
      />

      {showHistory && (
        <ConversationHistory onClose={() => setShowHistory(false)} />
      )}
    </div>
  );
};