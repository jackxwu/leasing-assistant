# Renter Chat Application Makefile

.PHONY: help install install-frontend install-backend start-frontend start-backend start dev clean

# Default target
help:
	@echo "Available targets:"
	@echo "  install          - Install all dependencies (frontend + backend)"
	@echo "  install-frontend - Install frontend dependencies only"
	@echo "  install-backend  - Install backend dependencies only"
	@echo "  start-frontend   - Start frontend development server"
	@echo "  start-backend    - Start backend development server"
	@echo "  start            - Start both frontend and backend (requires two terminals)"
	@echo "  dev              - Start both servers in parallel (single terminal)"
	@echo "  clean            - Clean dependencies and build files"

# Install all dependencies
install: install-backend install-frontend
	@echo "✅ All dependencies installed!"

# Install frontend dependencies
install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ Frontend dependencies installed!"

# Install backend dependencies
install-backend:
	@echo "🐍 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "✅ Backend dependencies installed!"

# Start frontend only
start-frontend:
	@echo "🚀 Starting frontend development server..."
	@echo "Frontend will be available at http://localhost:3000"
	cd frontend && npm start

# Start backend only
start-backend:
	@echo "🚀 Starting backend development server..."
	@echo "Backend will be available at http://localhost:8000"
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start both (requires two terminals)
start:
	@echo "🚀 Starting both servers..."
	@echo ""
	@echo "Run these commands in separate terminals:"
	@echo "Terminal 1: make start-backend"
	@echo "Terminal 2: make start-frontend"
	@echo ""
	@echo "Or use 'make dev' to run both in parallel"

# Start both servers in parallel (single terminal)
dev: install
	@echo "🚀 Starting both servers in parallel..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo ""
	@echo "Press Ctrl+C to stop both servers"
	@(cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &) && (cd frontend && npm start)

# Clean dependencies and build files
clean:
	@echo "🧹 Cleaning dependencies and build files..."
	rm -rf frontend/node_modules
	rm -rf frontend/build
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/app/*/__pycache__
	@echo "✅ Cleanup complete!"

# Quick development setup
setup: install
	@echo ""
	@echo "🎉 Setup complete! You can now run:"
	@echo "  make dev        - Start both servers in parallel"
	@echo "  make start-*    - Start individual servers"
	@echo ""