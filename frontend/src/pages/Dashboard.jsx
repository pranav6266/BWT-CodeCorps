import { useEffect, useState } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useApi } from '../services/api';
import { Wallet } from 'lucide-react';

const Dashboard = () => {
    const { getToken } = useAuth();
    const api = useApi(getToken);
    const [metrics, setMetrics] = useState(null);

    useEffect(() => {
        const fetchDashboardData = async () => {
            // In your backend, this would likely come from a 'user/status' or 'metrics' endpoint
            const res = await api.getExpenses();
            // Logic to calculate summaries...
        };
        fetchDashboardData();
    }, []);

    return (
        <div className="p-8 bg-slate-950 min-h-screen text-white">
            <header className="mb-10">
                <h1 className="text-3xl font-bold">Financial Overview</h1>
                <p className="text-slate-400">Grounded analysis of your current standing.</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Metric Card */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                    <div className="flex justify-between items-start mb-4">
                        <Wallet className="text-blue-400" />
                        <span className="text-xs font-mono text-slate-500">DTI RATIO</span>
                    </div>
                    <h2 className="text-4xl font-bold">32%</h2>
                    <p className="text-emerald-400 text-sm mt-2">Within safe limits</p>
                </div>

                {/* 3D Mini-Scene could go here: A progress bar that is a 3D tube */}
                <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl md:col-span-2">
                    <h3 className="font-semibold mb-4">Expense Distribution</h3>
                    <div className="h-32 flex items-end gap-2">
                        {/* Simple CSS bars for now, replace with 3D bars later */}
                        {[40, 70, 45, 90, 65].map((h, i) => (
                            <div key={i} style={{ height: `${h}%` }} className="flex-1 bg-blue-600/20 border-t-2 border-blue-500 rounded-t-sm" />
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export  default { Dashboard };