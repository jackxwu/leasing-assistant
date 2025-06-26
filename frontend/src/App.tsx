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

  // Start with completely empty preferences - let user specify them naturally
  const mockPreferences: Preferences | undefined = undefined;

  return (
    <div className="App">
      <ChatWorkspace
        lead={mockLead}
        preferences={mockPreferences}
        communityId="unknown"
      />
    </div>
  );
}

export default App;
