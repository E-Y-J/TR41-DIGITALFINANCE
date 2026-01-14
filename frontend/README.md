# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is enabled on this template. See [this documentation](https://react.dev/learn/react-compiler) for more information.

Note: This will impact Vite dev & build performances.

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

## Frontend Run Dev Instructions
1. Add .env file in the `frontend` directory with the following variables:

    ```env
    VITE_AUTH0_DOMAIN=******.auth0.com
    VITE_AUTH0_CLIENT_ID=******
    VITE_AUTH0_AUDIENCE=******
    ```

2.  Navigate to the `frontend` directory:

    ```bash
    cd frontend
    ```
3.  Install the required dependencies using npm or yarn:

    ```bash
    npm install
    ```
4. Open 2nd terminal and create a virtual environment for the backend:

    ```bash
    cd ../backend
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```    

5. Start the backend server:

    ```bash
    pip install -r requirements.txt

    # Create PostgreSQL database (or use SQLite for development)
    # PostgreSQL:
    # createdb digital_finance_db

    # Initialize migrations
    # flask db init

    # Create migration
    # flask db migrate -m "Initial migration"

    # Apply migration
    # flask db upgrade

    # Start the Flask development server
    flask run --port=8000
    ```

5.  Start the development server on the 1st terminal:

    ```bash 
    npm run dev
    ```
