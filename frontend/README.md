# Frontend - SecureBank AI Digital Finance Tracker

React-based single-page application for the AI Digital Finance Tracker.

## 🌐 Live Demo

**Production URL:** https://securebankai.vercel.app

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | React 19 |
| **Build Tool** | Vite 6 |
| **Language** | JavaScript/JSX |
| **UI Library** | MUI (Material UI) v6 |
| **State Management** | Redux Toolkit |
| **Data Fetching** | TanStack Query (React Query) |
| **Routing** | React Router v7 |
| **Authentication** | Auth0 React SDK |
| **HTTP Client** | Axios |
| **Charts** | Chart.js / Recharts |
| **Hosting** | Vercel |

---

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── api/               # API client and endpoints
│   ├── assets/            # Images, icons, static files
│   ├── auth/              # Auth0 provider and hooks
│   ├── components/        # Reusable UI components
│   ├── features/          # Feature-specific components
│   ├── guard/             # Route guards (auth protection)
│   ├── hooks/             # Custom React hooks
│   ├── layouts/           # Page layouts (dashboard, auth)
│   ├── pages/             # Page components
│   ├── utils/             # Utility functions
│   ├── App.jsx            # Main app component
│   ├── main.jsx           # Entry point
│   └── theme.ts           # MUI theme configuration
├── .env.example           # Environment variables template
├── package.json           # Dependencies and scripts
├── vite.config.js         # Vite configuration
└── eslint.config.js       # ESLint configuration
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Auth0 account (for authentication)

### Environment Variables

Create a `.env` file in the `frontend` directory:

```env
# Auth0 Configuration
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://your-api-audience

# API Configuration
VITE_API_URL=https://securebankai.mysticdatanode.net
# For local development:
# VITE_API_URL=http://localhost:8000
```

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

---

## 📜 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |

---

## 🔐 Authentication Flow

1. User clicks "Login" button
2. Auth0 Universal Login opens (account picker)
3. User authenticates via Google, GitHub, or email/password
4. Auth0 redirects to `/callback` with authorization code
5. Frontend exchanges code for tokens
6. Backend validates token and syncs user to database
7. User redirected to `/home` or `/onboarding` (if new)

### Auth0 Configuration

The Auth0 provider is configured in `src/auth/Auth0Provider.jsx`:

```jsx
<Auth0Provider
  domain={domain}
  clientId={clientId}
  authorizationParams={{
    redirect_uri: `${window.location.origin}/callback`,
    scope: "openid profile email",
    audience: audience,
    prompt: "select_account",  // Forces account picker
  }}
  cacheLocation="memory"
>
```

---

## 🎨 Key Features

### Dashboard
- Financial overview with balance summaries
- Recent transactions list
- Spending trends chart
- Budget status indicators

### Transactions
- Add/edit/delete transactions
- AI-powered auto-categorization
- Filter by date, category, type
- Paginated transaction history

### AI Chat
- Natural language financial assistant
- Ask about spending, budgets, trends
- Execute commands via chat (add transaction, check budget)

### Budgets
- Create spending limits by category
- Visual progress indicators
- Alert notifications when approaching limits

### Profile & Settings
- Update personal information
- Currency preferences
- Notification settings

---

## 🧪 Testing

```bash
# Run linting
npm run lint

# Type checking (if using TypeScript)
npm run typecheck
```

For E2E tests, see `shared/e2e/README.md` (Playwright).

---

## 🚀 Deployment

The frontend auto-deploys to Vercel on push to `main` branch.

### Manual Deployment

```bash
# Build production bundle
npm run build

# Preview locally
npm run preview

# Deploy to Vercel
npx vercel --prod
```

---

## 🔗 Related Documentation

- [Main Project README](../README.md)
- [Backend README](../backend/README.md)
- [API Documentation](https://securebankai.mysticdatanode.net/api/docs/)
- [E2E Tests](../shared/e2e/README.md)
