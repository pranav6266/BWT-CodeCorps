import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

let tokenGetter = null;

export const setTokenGetter = (getterFn) => {
    tokenGetter = getterFn;
};

api.interceptors.request.use(async (config) => {
    if (!tokenGetter) {
        console.warn('[API] No token getter set yet');
        return config;
    }
    
    try {
        const token = await tokenGetter();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
            console.log('[API] Token set in headers:', token.substring(0, 20) + '...');
        } else {
            console.warn('[API] Token is null/undefined');
        }
    } catch (error) {
        console.error('[API] Error getting token:', error);
    }
    return config;
});

api.interceptors.response.use(
    response => {
        console.log('[API] Response:', response.config.url, response.status);
        return response;
    },
    error => {
        console.error('[API] Error response:', error.config?.url, error.response?.status, error.response?.data);
        return Promise.reject(error);
    }
);

export const useApi = (getToken) => {
    if (getToken) {
        setTokenGetter(getToken);
    }

    return {
        getProfile: () => api.get('/profile'),
        updateProfile: (data) => api.post('/profile', data),
        getExpenses: () => api.get('/expenses'),
        addExpense: (data) => api.post('/expenses', data),
        deleteExpense: (id) => api.delete(`/expenses/${id}`),
        evaluateDecision: (decisionData) => api.post('/evaluate-decision', decisionData),
        sendMessage: (message) => api.post('/chat', { message }),
    };
};

export default api;
