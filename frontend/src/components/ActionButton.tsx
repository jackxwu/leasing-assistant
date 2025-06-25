import React from 'react';
import { ChatResponse } from '../types/chat';
import './ActionButton.css';

interface ActionButtonProps {
  response: ChatResponse;
  onActionClick: (action: string, data?: any) => void;
}

export const ActionButton: React.FC<ActionButtonProps> = ({ response, onActionClick }) => {
  const renderActionButton = () => {
    switch (response.action) {
      case 'propose_tour':
        const tourTime = response.proposed_time 
          ? new Date(response.proposed_time).toLocaleString()
          : 'the proposed time';
        return (
          <button 
            className="action-button propose-tour"
            onClick={() => onActionClick('confirm_tour', { time: response.proposed_time })}
          >
            Confirm Tour at {tourTime}
          </button>
        );
      
      case 'ask_clarification':
        return (
          <div className="clarification-prompt">
            <span className="clarification-text">Please provide more details</span>
          </div>
        );
      
      case 'handoff_human':
        return (
          <button 
            className="action-button handoff"
            onClick={() => onActionClick('connect_human')}
          >
            Connect with Human Agent
          </button>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="action-container">
      {renderActionButton()}
    </div>
  );
};