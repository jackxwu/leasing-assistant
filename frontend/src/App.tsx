import React from 'react';
import { ChatWorkspace } from './components/ChatWorkspace';
import { Lead, Preferences } from './types/chat';
import './App.css';

function App() {
  // Mock data - in a real app, this would come from props, context, or API
  const mockLead: Lead = {
    name: "Jane Doe",
    email: "jane@example.com"
  };

  const mockPreferences: Preferences = {
    bedrooms: 2,
    move_in: "2025-07-01"
  };

  return (
    <div className="App">
      <ChatWorkspace
        lead={mockLead}
        preferences={mockPreferences}
        communityId="sunset-ridge"
      />
    </div>
  );
}

export default App;
