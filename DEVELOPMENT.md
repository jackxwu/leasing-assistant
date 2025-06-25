# Development Guide

This guide contains setup instructions, testing procedures, and development workflows for the Renter Chat Application.

## Prerequisites

- Node.js (v14 or higher)
- Python 3.8+
- pip package manager

## Installation & Setup

### Option 1: Using Makefile (Recommended)

```bash
# Install all dependencies
make setup

# Start both servers in parallel
make dev
```

### Option 2: Manual Setup

#### 1. Start the Backend Server

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python -m app.main
```

The backend will start on `http://localhost:8000`

#### 2. Start the Frontend Server

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will start on `http://localhost:3000` and automatically open in your browser.

## Available Make Commands

### **Setup & Installation:**
- `make install` - Install all dependencies (frontend + backend)
- `make install-frontend` - Install frontend dependencies only  
- `make install-backend` - Install backend dependencies only

### **Development Servers:**
- `make start-backend` - Start backend server only
- `make start-frontend` - Start frontend server only
- `make dev` - **Start both servers in parallel (recommended)**

### **Utilities:**
- `make help` - Show all available commands
- `make clean` - Clean all dependencies and build files
- `make setup` - Full setup (install + instructions)

## Manual UI Testing Guide

### Test Scenarios

Once both servers are running, you can test these conversation flows:

#### 1. **Unit Availability & Tour Scheduling**
- **Message**: "Is a 2-bedroom available?"
- **Expected**: Shows available units with pricing and tour time options
- **Action**: Click "Confirm Tour" button to test tour scheduling

#### 2. **Pet Policy Inquiry**
- **Message**: "Do you allow cats?"
- **Expected**: Pet-friendly policy with tour scheduling
- **Action**: Tour scheduling button appears

#### 3. **Pricing Questions**
- **Message**: "What are your rent prices?"
- **Expected**: Price ranges with clarification prompt
- **Action**: "Ask clarification" response (no action button)

#### 4. **Amenity Information**
- **Message**: "What amenities do you have?"
- **Expected**: Detailed amenity list with tour offer
- **Action**: Tour scheduling button

#### 5. **Move-in Timeline**
- **Message**: "When can I move in?"
- **Expected**: Availability info with clarification request
- **Action**: Clarification prompt (no button)

#### 6. **Application Process**
- **Message**: "How do I apply?"
- **Expected**: Application requirements with human handoff
- **Action**: "Connect with Human Agent" button

#### 7. **Short/Unclear Messages**
- **Message**: "Hi" or "Help"
- **Expected**: Helpful clarification prompt
- **Action**: Clarification response (no button)

### UI Elements to Test

- **Message Display**: Check user vs agent message styling
- **Timestamps**: Verify message timestamps appear correctly
- **Loading State**: Look for typing indicator during API calls
- **Action Buttons**: Test all three action types
- **Input Field**: Try typing and sending messages
- **Scrolling**: Verify auto-scroll to new messages
- **Responsive Design**: Test on different screen sizes

### Testing Different Scenarios

**Multi-keyword Messages:**
- "Is a 2-bedroom available and do you allow pets?"
- "What's the price range for your 1-bedroom units?"
- "I'm looking to move in July, what's available?"

**Edge Cases:**
- Empty messages (should be disabled)
- Very long messages
- Special characters
- Multiple rapid messages

### Expected Behavior

- Messages appear instantly for user, with typing indicator for agent
- Action buttons appear only when relevant
- Tour confirmations show success messages
- Human handoff shows connection message
- All interactions feel natural and responsive

## Troubleshooting

### Common Issues

**If frontend won't load:**
- Check that backend is running on port 8000
- Verify no CORS errors in browser console
- Try refreshing the page

**If messages don't send:**
- Check browser network tab for API errors
- Verify backend logs for error messages
- Ensure both servers are running

**If dependencies fail to install:**
- Check Node.js and Python versions meet requirements
- Try clearing caches: `make clean` then `make install`
- For Python issues, consider using a virtual environment

### Port Conflicts

If ports 3000 or 8000 are already in use:
- Frontend: Set `PORT=3001` environment variable
- Backend: Modify `port=8000` in `backend/app/main.py`

## Development Notes

### Backend
- Uses realistic fake data for testing purposes
- Agent responses are keyword-based and deterministic
- Tour times are dynamically generated for the next few days
- All endpoints include CORS headers for frontend communication

### Frontend
- Includes mock lead data (Jane Doe, 2-bedroom preference)
- TypeScript strict mode enabled
- Components are modular and reusable
- CSS uses responsive design principles

### Testing Data

The backend includes fake data for:
- 4 different apartment units with varying specs
- 5 tour time slots over the next few days
- Keyword-based response logic for different inquiry types

## Project Structure Details

```
├── frontend/
│   ├── public/            # Static assets
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── ChatWorkspace.tsx    # Main chat interface
│   │   │   ├── ChatMessage.tsx      # Message component
│   │   │   ├── ChatInput.tsx        # Input component
│   │   │   └── ActionButton.tsx     # Action buttons
│   │   ├── types/         # TypeScript definitions
│   │   ├── services/      # API service layer
│   │   └── App.tsx        # Main app component
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py           # API endpoints
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── services/
│   │   │   └── agent.py            # Business logic
│   │   └── main.py                 # FastAPI app
│   └── requirements.txt            # Python dependencies
├── Makefile                        # Development automation
├── .gitignore                      # Git ignore rules
├── README.md                       # Project overview
└── DEVELOPMENT.md                  # This file
```