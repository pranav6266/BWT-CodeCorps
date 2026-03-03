import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

// Helper to inject Clerk Token into every request
export const useApi = (getToken) => {
    api.interceptors.request.use(async (config) => {
        const token = await getToken();
        config.headers.Authorization = `Bearer ${token}`;
        return config;
    });

    return {
        // Expense Routes
        getExpenses: () => api.get('/expenses'),
        addExpense: (data) => api.post('/expenses', data),

        // Decision Routes (The core logic)
        evaluateDecision: (decisionData) => api.post('/evaluate-decision', decisionData),

        // Chat Routes
        sendMessage: (message) => api.post('/chat', { message }),
    };
};

export default api;