import React, { useEffect, useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useApi } from '../services/api';
import { Wallet, PieChart, Plus, Trash2, List, UserCircle } from 'lucide-react';

const Dashboard = () => {
    const { getToken } = useAuth();
    const api = useApi(getToken);

    const [expenses, setExpenses] = useState([]);
    const [categoryTotals, setCategoryTotals] = useState({});
    const [loading, setLoading] = useState(true);

    // Profile State
    const [profile, setProfile] = useState({ monthly_income: 0, current_debt: 0, savings_rate: 0 });
    const [isSavingProfile, setIsSavingProfile] = useState(false);

    // Expense Form State
    const [amount, setAmount] = useState('');
    const [category, setCategory] = useState('Food & Groceries');
    const [description, setDescription] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const fetchData = async () => {
        try {
            // Fetch Expenses
            const expRes = await api.getExpenses();
            setExpenses(expRes.data);
            const totals = expRes.data.reduce((acc, curr) => {
                acc[curr.category] = (acc[curr.category] || 0) + curr.amount;
                return acc;
            }, {});
            setCategoryTotals(totals);

            // Fetch Profile
            const profRes = await api.getProfile();
            setProfile({
                monthly_income: profRes.data.monthly_income || 0,
                current_debt: profRes.data.current_debt || 0,
                savings_rate: profRes.data.savings_rate || 0
            });
        } catch (error) {
            console.error("Failed to fetch data:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleSaveProfile = async (e) => {
        e.preventDefault();
        setIsSavingProfile(true);
        try {
            await api.updateProfile({
                monthly_income: parseFloat(profile.monthly_income),
                current_debt: parseFloat(profile.current_debt),
                savings_rate: parseFloat(profile.savings_rate)
            });
            alert("Profile saved successfully!");
        } catch (error) {
            console.error("Failed to save profile", error);
        } finally {
            setIsSavingProfile(false);
        }
    };

    const handleAddExpense = async (e) => { /* ... keep your existing add logic ... */ };
    const handleDeleteExpense = async (id) => { /* ... keep your existing delete logic ... */ };

    const maxCategoryAmount = Math.max(...Object.values(categoryTotals), 1);
    const totalSpent = expenses.reduce((sum, exp) => sum + exp.amount, 0);

    return (
        <div className="p-8 bg-slate-950 min-h-screen text-white mt-10 max-w-7xl mx-auto">
            <header className="mb-10">
                <h1 className="text-3xl font-bold">Financial Overview</h1>
                <p className="text-slate-400">Grounded analysis of your current standing.</p>
            </header>

            {/* Top Section: Metrics and Profile */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">

                {/* Profile Card (NEW) */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl flex flex-col justify-between">
                    <div className="flex items-center gap-2 mb-4">
                        <UserCircle className="text-blue-400" />
                        <h3 className="font-semibold text-sm text-slate-400 uppercase tracking-wider">Your Base Profile</h3>
                    </div>
                    <form onSubmit={handleSaveProfile} className="space-y-3">
                        <div>
                            <label className="text-xs text-slate-500">Monthly Income (₹)</label>
                            <input
                                type="number"
                                value={profile.monthly_income}
                                onChange={(e) => setProfile({...profile, monthly_income: e.target.value})}
                                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1 text-sm outline-none focus:border-blue-500"
                            />
                        </div>
                        <div>
                            <label className="text-xs text-slate-500">Current Monthly EMI/Debt (₹)</label>
                            <input
                                type="number"
                                value={profile.current_debt}
                                onChange={(e) => setProfile({...profile, current_debt: e.target.value})}
                                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1 text-sm outline-none focus:border-blue-500"
                            />
                        </div>
                        <div>
                            <label className="text-xs text-slate-500">Target Savings Rate (%)</label>
                            <input
                                type="number"
                                value={profile.savings_rate}
                                onChange={(e) => setProfile({...profile, savings_rate: e.target.value})}
                                className="w-full bg-slate-950 border border-slate-800 rounded px-3 py-1 text-sm outline-none focus:border-blue-500"
                            />
                        </div>
                        <button
                            disabled={isSavingProfile}
                            className="w-full bg-blue-600/20 text-blue-400 hover:bg-blue-600 hover:text-white py-1.5 rounded text-sm font-semibold transition-colors mt-2"
                        >
                            {isSavingProfile ? 'Saving...' : 'Save Profile Base'}
                        </button>
                    </form>
                </div>

                {/* Dashboard Stats */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl lg:col-span-2">
                    <div className="flex flex-col h-full">
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <span className="text-xs font-mono text-slate-500">TOTAL SPENT THIS MONTH</span>
                                <h2 className="text-4xl font-bold mt-1 text-red-400">₹{totalSpent.toLocaleString()}</h2>
                            </div>
                            <div className="text-right">
                                <span className="text-xs font-mono text-slate-500">ESTIMATED REMAINING</span>
                                <h2 className="text-2xl font-bold mt-1 text-emerald-400">
                                    ₹{Math.max(0, profile.monthly_income - profile.current_debt - totalSpent).toLocaleString()}
                                </h2>
                            </div>
                        </div>

                        {/* Keep your existing Expense Distribution Chart here */}
                        <div className="flex-1 mt-auto">
                            <div className="flex items-center gap-2 mb-2">
                                <PieChart size={16} className="text-purple-400" />
                                <h3 className="text-sm font-semibold text-slate-400">Expense Distribution</h3>
                            </div>
                            {/* ... the rest of your dynamic chart mapping ... */}
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Section: Add Expense & List */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Create Expense Form */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl lg:col-span-1 h-fit">
                    <div className="flex items-center gap-2 mb-6">
                        <Plus className="text-emerald-400" />
                        <h3 className="font-bold text-lg">Log New Expense</h3>
                    </div>
                    <form onSubmit={handleAddExpense} className="space-y-4">
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Amount (₹)</label>
                            <input
                                type="number"
                                required
                                value={amount}
                                onChange={(e) => setAmount(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 outline-none focus:border-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Category</label>
                            <select
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 outline-none focus:border-blue-500"
                            >
                                <option>Food & Groceries</option>
                                <option>Transport</option>
                                <option>Utilities & Bills</option>
                                <option>Housing</option>
                                <option>Entertainment</option>
                                <option>Healthcare</option>
                                <option>Other</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Description (Optional)</label>
                            <input
                                type="text"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="e.g., Weekly groceries"
                                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 outline-none focus:border-blue-500"
                            />
                        </div>
                        <button
                            disabled={isSubmitting}
                            className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded-lg font-bold transition-colors disabled:opacity-50 mt-4"
                        >
                            {isSubmitting ? 'Saving...' : 'Add Expense'}
                        </button>
                    </form>
                </div>

                {/* Expense List (Read & Delete) */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl lg:col-span-2">
                    <div className="flex items-center gap-2 mb-6">
                        <List className="text-blue-400" />
                        <h3 className="font-bold text-lg">Recent Transactions</h3>
                    </div>

                    <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                        {expenses.length === 0 && !loading ? (
                            <div className="text-center py-10 text-slate-500">No transactions found. Start logging!</div>
                        ) : (
                            expenses.slice().reverse().map((exp) => (
                                <div key={exp._id} className="flex justify-between items-center p-4 bg-slate-950/50 border border-slate-800/50 rounded-xl hover:border-slate-700 transition-colors">
                                    <div>
                                        <p className="font-semibold text-slate-200">{exp.category}</p>
                                        {exp.description && <p className="text-sm text-slate-500">{exp.description}</p>}
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <span className="font-bold text-lg">₹{exp.amount.toLocaleString()}</span>
                                        <button
                                            onClick={() => handleDeleteExpense(exp._id)}
                                            className="p-2 text-slate-500 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
                                            title="Delete Expense"
                                        >
                                            <Trash2 size={18} />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Dashboard;