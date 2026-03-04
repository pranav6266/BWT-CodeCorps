import React, { useState, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useApi } from '../services/api';

const Dashboard = () => {
    const { getToken, isLoaded } = useAuth();
    const api = useApi(getToken);

    const [profile, setProfile] = useState({
        monthlyIncome: '',
        currentEmi: '',
        targetSavingsRate: '',
    });

    const [expenses, setExpenses] = useState([]);
    const [newExpense, setNewExpense] = useState({
        title: '',
        amount: '',
        category: 'Food & Groceries',
    });

    const [profileError, setProfileError] = useState('');
    const [expenseError, setExpenseError] = useState('');
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        if (isLoaded) {
            fetchData();
        }
    }, [isLoaded]);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const token = await getToken();
            console.log('[Dashboard] Fetching data with token:', token ? 'Token present' : 'NO TOKEN');

            const profileRes = await api.getProfile();
            console.log('[Dashboard] Profile response:', profileRes.data);
            
            if (profileRes.data) {
                const data = profileRes.data;
                setProfile({
                    monthlyIncome: data.monthlyIncome !== undefined && data.monthlyIncome !== null ? String(data.monthlyIncome) : '',
                    currentEmi: data.currentEmi !== undefined && data.currentEmi !== null ? String(data.currentEmi) : '',
                    targetSavingsRate: data.targetSavingsRate !== undefined && data.targetSavingsRate !== null ? String(data.targetSavingsRate) : ''
                });
            }

            const expensesRes = await api.getExpenses();
            console.log('[Dashboard] Expenses response:', expensesRes.data);
            
            if (expensesRes.data) {
                const mappedExpenses = expensesRes.data.map(exp => ({
                    ...exp,
                    title: exp.title || exp.description || ''
                }));
                setExpenses(mappedExpenses);
            }
        } catch (error) {
            console.error('[Dashboard] Error fetching data:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const validateProfile = () => {
        const income = parseFloat(profile.monthlyIncome);
        const emi = parseFloat(profile.currentEmi);
        const savings = parseFloat(profile.targetSavingsRate);

        if (isNaN(income) || income <= 0) {
            return 'Please enter a valid monthly income greater than 0';
        }
        if (isNaN(emi) || emi < 0) {
            return 'Please enter a valid EMI amount (0 or greater)';
        }
        if (isNaN(savings) || savings < 0 || savings > 100) {
            return 'Please enter a valid savings rate (0-100%)';
        }
        return null;
    };

    const validateExpense = () => {
        const amount = parseFloat(newExpense.amount);
        if (!newExpense.title.trim()) {
            return 'Please enter a title for the expense';
        }
        if (isNaN(amount) || amount <= 0) {
            return 'Please enter a valid amount greater than 0';
        }
        return null;
    };

    const handleProfileChange = (e) => {
        setProfile({ ...profile, [e.target.name]: e.target.value });
        setProfileError('');
    };

    const handleExpenseChange = (e) => {
        setNewExpense({ ...newExpense, [e.target.name]: e.target.value });
        setExpenseError('');
    };

    const handleProfileSubmit = async (e) => {
        e.preventDefault();
        
        const validationError = validateProfile();
        if (validationError) {
            setProfileError(validationError);
            return;
        }

        try {
            const profileData = {
                monthly_income: parseFloat(profile.monthlyIncome),
                current_debt: parseFloat(profile.currentEmi),
                savings_rate: parseFloat(profile.targetSavingsRate)
            };

            console.log('[Dashboard] Saving profile:', profileData);
            const res = await api.updateProfile(profileData);
            console.log('[Dashboard] Save response:', res.data);

            if (res.data) {
                const data = res.data;
                setProfile({
                    monthlyIncome: data.monthlyIncome !== undefined && data.monthlyIncome !== null ? String(data.monthlyIncome) : profile.monthlyIncome,
                    currentEmi: data.currentEmi !== undefined && data.currentEmi !== null ? String(data.currentEmi) : profile.currentEmi,
                    targetSavingsRate: data.targetSavingsRate !== undefined && data.targetSavingsRate !== null ? String(data.targetSavingsRate) : profile.targetSavingsRate
                });
            }
            alert('Profile updated successfully!');
        } catch (error) {
            console.error('[Dashboard] Error saving profile:', error);
            setProfileError('Failed to save profile. Please try again.');
        }
    };

    const handleExpenseSubmit = async (e) => {
        e.preventDefault();

        const validationError = validateExpense();
        if (validationError) {
            setExpenseError(validationError);
            return;
        }

        try {
            const expenseData = {
                amount: parseFloat(newExpense.amount),
                category: newExpense.category,
                title: newExpense.title,
                description: newExpense.title
            };

            const res = await api.addExpense(expenseData);

            if (res.data) {
                const newExp = {
                    ...res.data,
                    title: res.data.title || newExpense.title,
                    amount: res.data.amount || newExpense.amount,
                    category: res.data.category || newExpense.category
                };
                setExpenses([...expenses, newExp]);
            }

            setNewExpense({ title: '', amount: '', category: 'Food & Groceries' });
        } catch (error) {
            console.error('[Dashboard] Error adding expense:', error);
            setExpenseError('Failed to add expense. Please try again.');
        }
    };

    const handleDeleteExpense = async (id) => {
        try {
            await api.deleteExpense(id);
            setExpenses(expenses.filter(exp => exp.id !== id && exp._id !== id));
        } catch (error) {
            console.error('Error deleting expense:', error);
        }
    };

    const totalSpent = expenses.reduce((acc, curr) => acc + Number(curr.amount), 0);
    const estimatedRemaining = Number(profile.monthlyIncome) - Number(profile.currentEmi) - totalSpent;

    if (!isLoaded || isLoading) {
        return (
            <div className="p-6 max-w-6xl mx-auto">
                <p className="text-center text-gray-500">Loading...</p>
            </div>
        );
    }

    return (
        <div className="p-6 max-w-6xl mx-auto space-y-8">
            <h1 className="text-3xl font-bold">Financial Dashboard</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="p-6 border rounded shadow">
                    <h2 className="text-xl font-semibold mb-4">Financial Profile</h2>
                    <form onSubmit={handleProfileSubmit} className="space-y-4">
                        <div>
                            <label className="block mb-1">Monthly Income</label>
                            <input
                                type="number"
                                name="monthlyIncome"
                                value={profile.monthlyIncome}
                                onChange={handleProfileChange}
                                className="w-full border p-2 rounded"
                                placeholder="Enter your monthly income"
                                required
                            />
                        </div>
                        <div>
                            <label className="block mb-1">Current Monthly EMI</label>
                            /Debt<input
                                type="number"
                                name="currentEmi"
                                value={profile.currentEmi}
                                onChange={handleProfileChange}
                                className="w-full border p-2 rounded"
                                placeholder="Enter your current monthly EMI"
                                required
                            />
                        </div>
                        <div>
                            <label className="block mb-1">Target Savings Rate (%)</label>
                            <input
                                type="number"
                                name="targetSavingsRate"
                                value={profile.targetSavingsRate}
                                onChange={handleProfileChange}
                                className="w-full border p-2 rounded"
                                placeholder="Enter target savings rate (0-100)"
                                min="0"
                                max="100"
                                required
                            />
                        </div>
                        {profileError && (
                            <p className="text-red-500 text-sm">{profileError}</p>
                        )}
                        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                            Save Profile
                        </button>
                    </form>
                </div>

                <div className="p-6 border rounded shadow">
                    <h2 className="text-xl font-semibold mb-4">Log New Expense</h2>
                    <form onSubmit={handleExpenseSubmit} className="space-y-4">
                        <div>
                            <label className="block mb-1">Title</label>
                            <input
                                type="text"
                                name="title"
                                value={newExpense.title}
                                onChange={handleExpenseChange}
                                className="w-full border p-2 rounded"
                                placeholder="e.g., Grocery shopping"
                                required
                            />
                        </div>
                        <div>
                            <label className="block mb-1">Amount</label>
                            <input
                                type="number"
                                name="amount"
                                value={newExpense.amount}
                                onChange={handleExpenseChange}
                                className="w-full border p-2 rounded"
                                placeholder="Enter amount"
                                required
                            />
                        </div>
                        <div>
                            <label className="block mb-1">Category</label>
                            <select
                                name="category"
                                value={newExpense.category}
                                onChange={handleExpenseChange}
                                className="w-full border p-2 rounded"
                            >
                                <option value="Food & Groceries">Food & Groceries</option>
                                <option value="Transport">Transport</option>
                                <option value="Utilities & Bills">Utilities & Bills</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        {expenseError && (
                            <p className="text-red-500 text-sm">{expenseError}</p>
                        )}
                        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
                            Add Expense
                        </button>
                    </form>
                </div>
            </div>

            <div className="p-6 border rounded shadow bg-gray-50">
                <h2 className="text-xl font-semibold mb-4">Overview</h2>
                <div className="flex flex-col space-y-2 mb-6">
                    <p className="text-lg">Total Spent This Month: <span className="font-bold text-red-600">${totalSpent}</span></p>
                    <p className="text-lg">Estimated Remaining: <span className="font-bold text-green-600">${estimatedRemaining ? estimatedRemaining : 0}</span></p>
                </div>

                <h3 className="text-lg font-semibold mt-4 mb-2">Recent Expenses</h3>
                <ul className="divide-y border rounded p-4 bg-white">
                    {expenses.length === 0 ? (
                        <p className="text-gray-500">No expenses logged yet.</p>
                    ) : (
                        expenses.map((exp, index) => (
                            <li key={exp.id || exp._id || index} className="py-2 flex justify-between items-center">
                                <span>{exp.title || exp.description} <span className="text-sm text-gray-500">({exp.category})</span></span>
                                <div className="flex items-center gap-3">
                                    <span className="font-semibold text-gray-800">${exp.amount}</span>
                                    <button 
                                        onClick={() => handleDeleteExpense(exp.id || exp._id)}
                                        className="text-red-500 hover:text-red-700 text-sm"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </li>
                        ))
                    )}
                </ul>
            </div>
        </div>
    );
};

export default Dashboard;
