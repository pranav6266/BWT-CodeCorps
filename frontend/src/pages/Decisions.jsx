import { useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useApi } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

const Decisions = () => {
    const { getToken } = useAuth();
    const api = useApi(getToken);

    const [amount, setAmount] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleEvaluate = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            // Sending to your FastAPI backend
            const res = await api.evaluateDecision({ new_monthly_obligation: parseFloat(amount) });
            setResult(res.data);
        } catch (err) {
            console.error("Evaluation failed", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-8 text-white">
            <h2 className="text-3xl font-bold mb-2">Decision Evaluator</h2>
            <p className="text-slate-400 mb-8">Test the impact of a new expense before you commit.</p>

            <form onSubmit={handleEvaluate} className="bg-slate-900 p-6 rounded-2xl border border-slate-800 mb-10">
                <label className="block text-sm font-medium mb-2">New Monthly EMI/Expense (₹)</label>
                <div className="flex gap-4">
                    <input
                        type="number"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
                        placeholder="e.g. 2000"
                        required
                    />
                    <button
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold transition-all disabled:opacity-50"
                    >
                        {loading ? 'Analyzing...' : 'Check Risk'}
                    </button>
                </div>
            </form>

            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`p-6 rounded-2xl border ${
                            result.risk_level === 'High' ? 'bg-red-900/20 border-red-500/50' :
                                result.risk_level === 'Moderate' ? 'bg-yellow-900/20 border-yellow-500/50' :
                                    'bg-emerald-900/20 border-emerald-500/50'
                        }`}
                    >
                        <div className="flex items-center gap-3 mb-4">
                            {result.risk_level === 'High' ? <AlertCircle className="text-red-500" /> : <CheckCircle className="text-emerald-500" />}
                            <h3 className="text-2xl font-bold">{result.risk_level} Risk</h3>
                        </div>
                        <p className="text-lg mb-4">Projected Debt-to-Income (DTI): <strong>{result.projected_dti.toFixed(1)}%</strong></p>
                        <div className="bg-black/30 p-4 rounded-lg italic text-slate-300">
                            "Based on your current savings rate and income, this obligation {result.risk_level === 'High' ? 'exceeds safety limits' : 'is manageable'}."
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
export default {Decisions};