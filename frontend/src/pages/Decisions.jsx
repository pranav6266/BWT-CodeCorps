import React, { useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useApi } from '../services/api';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle, Info } from 'lucide-react';

const Decisions = () => {
    const { getToken } = useAuth();
    const api = useApi(getToken);

    const [amount, setAmount] = useState('');
    const [decisionType, setDecisionType] = useState('New EMI');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleEvaluate = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload = {
                decision_type: decisionType,
                amount: parseFloat(amount)
            };
            const res = await api.evaluateDecision(payload);
            setResult(res.data);
        } catch (err) {
            console.error("Evaluation failed", err);
            setResult({
                warning: true,
                message: "Something went wrong. Please try again later.",
                risk_level: "Error"
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto p-8 text-white mt-10">
            <h2 className="text-3xl font-bold mb-2">Decision Evaluator</h2>
            <p className="text-slate-400 mb-8">Test the impact of a new expense before you commit.</p>

            <form onSubmit={handleEvaluate} className="bg-slate-900 p-6 rounded-2xl border border-slate-800 mb-10">
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                    <div>
                        <label className="block text-sm font-medium mb-2 text-slate-300">Decision Category</label>
                        <select
                            value={decisionType}
                            onChange={(e) => setDecisionType(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none appearance-none"
                        >
                            <option value="New EMI">New EMI (Loan/Financing)</option>
                            <option value="Vehicle Loan">Vehicle Loan</option>
                            <option value="Medical Emergency">Medical Emergency</option>
                            <option value="Major Purchase">Major Purchase</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium mb-2 text-slate-300">New Monthly EMI/Expense (₹)</label>
                        <input
                            type="number"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="e.g. 2000"
                            required
                        />
                    </div>
                </div>

                <button
                    disabled={loading || !amount}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg font-bold transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                    {loading ? 'Analyzing Impact...' : 'Check Risk'}
                </button>
            </form>

            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className={`p-6 rounded-2xl border ${
                            result.warning ? 'bg-blue-900/20 border-blue-500/50' :
                            result.risk_level === 'High' ? 'bg-red-900/20 border-red-500/50' :
                                result.risk_level === 'Moderate' ? 'bg-yellow-900/20 border-yellow-500/50' :
                                    'bg-emerald-900/20 border-emerald-500/50'
                        }`}
                    >
                        <div className="flex items-center gap-3 mb-4">
                            {result.warning ? (
                                <>
                                    <Info className="text-blue-500" />
                                    <h3 className="text-2xl font-bold">Action Required</h3>
                                </>
                            ) : result.risk_level === 'High' ? (
                                <>
                                    <AlertCircle className="text-red-500" />
                                    <h3 className="text-2xl font-bold">{result.risk_level} Risk</h3>
                                </>
                            ) : (
                                <>
                                    <CheckCircle className="text-emerald-500" />
                                    <h3 className="text-2xl font-bold">{result.risk_level} Risk</h3>
                                </>
                            )}
                        </div>

                        {result.warning ? (
                            <div className="bg-black/30 p-4 rounded-lg text-slate-300 leading-relaxed">
                                <p className="text-lg mb-2">{result.message}</p>
                                <p className="text-sm text-slate-400 mt-4">
                                    Please go to the <span className="text-blue-400">Dashboard</span> and set up your 
                                    financial profile with your monthly income, current EMI/debt, and target savings rate.
                                </p>
                            </div>
                        ) : (
                            <>
                                <p className="text-lg mb-4">
                                    Projected Debt-to-Income (DTI): <strong>{result.metrics_at_evaluation?.projected_dti_percentage?.toFixed(1) || 0}%</strong>
                                </p>

                                <div className="bg-black/30 p-4 rounded-lg italic text-slate-300 leading-relaxed">
                                    "{result.ai_explanation}"
                                </div>
                            </>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default Decisions;
