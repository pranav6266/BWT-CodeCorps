import { SignInButton, useUser } from "@clerk/clerk-react";
import { motion } from "framer-motion";
import FinancialHero from "../components/canvas/FinancialHero";
import { ArrowRight, ShieldCheck, TrendingUp, MessageSquare } from "lucide-react";

const Landing = () => {
    const { isSignedIn } = useUser();

    return (
        <div className="bg-slate-950 text-white min-h-screen overflow-hidden">
            {/* Navigation */}
            <nav className="p-6 flex justify-between items-center max-w-7xl mx-auto">
                <h1 className="text-2xl font-bold tracking-tighter bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
                    FIN-GUARD AI
                </h1>
                {isSignedIn ? (
                    <a href="/dashboard" className="bg-blue-600 px-6 py-2 rounded-full">Go to Dashboard</a>
                ) : (
                    <SignInButton mode="modal">
                        <button className="border border-slate-700 px-6 py-2 rounded-full hover:bg-slate-800 transition">Sign In</button>
                    </SignInButton>
                )}
            </nav>

            {/* Hero Section */}
            <main className="max-w-7xl mx-auto grid lg:grid-cols-2 items-center px-6">
                <motion.div
                    initial={{ opacity: 0, x: -50 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.8 }}
                >
                    <h2 className="text-6xl font-extrabold leading-tight mb-6">
                        Financial Safety <br />
                        <span className="text-blue-500">Grounded in Data.</span>
                    </h2>
                    <p className="text-slate-400 text-xl mb-8 max-w-md">
                        The AI-powered assistant designed for low-income households to make safer, smarter financial decisions. [cite: 1, 23]
                    </p>
                    <div className="flex gap-4">
                        <button className="bg-blue-600 hover:bg-blue-700 px-8 py-4 rounded-xl font-semibold flex items-center gap-2 transition-all">
                            Get Started Free <ArrowRight size={20} />
                        </button>
                    </div>
                </motion.div>

                {/* 3D Visual Layer */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 1 }}
                >
                    <FinancialHero />
                </motion.div>
            </main>

            {/* Feature Grid - Mapped to your Backend Routes */}
            <section className="max-w-7xl mx-auto py-24 px-6 grid md:grid-cols-3 gap-8">
                <FeatureCard
                    icon={<TrendingUp className="text-emerald-400" />}
                    title="Expense Tracking"
                    desc="Log and categorize daily spending to monitor your disposable income. [cite: 81]"
                />
                <FeatureCard
                    icon={<ShieldCheck className="text-blue-400" />}
                    title="Risk Evaluation"
                    desc="Rule-based assessment for major decisions like new EMIs. [cite: 81]"
                />
                <FeatureCard
                    icon={<MessageSquare className="text-purple-400" />}
                    title="Contextual AI Chat"
                    desc="Get explanations for financial risks grounded in your specific data. [cite: 81]"
                />
            </section>
        </div>
    );
};

const FeatureCard = ({ icon, title, desc }) => (
    <div className="bg-slate-900/50 border border-slate-800 p-8 rounded-2xl hover:border-blue-500/50 transition-colors">
        <div className="mb-4">{icon}</div>
        <h3 className="text-xl font-bold mb-2">{title}</h3>
        <p className="text-slate-400 leading-relaxed">{desc}</p>
    </div>
);

export default Landing;