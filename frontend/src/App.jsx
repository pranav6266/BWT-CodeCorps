import { Routes, Route, Navigate } from 'react-router-dom';
import { SignedIn, SignedOut, UserButton } from '@clerk/clerk-react';
import Landing from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import Decisions from './pages/Decisions';
import Chat from './pages/Chat';
import { Canvas } from '@react-three/fiber';
import { Stars } from '@react-three/drei';

// A subtle 3D background that stays behind all pages
const SceneBg = () => (
    <div className="fixed inset-0 -z-10 pointer-events-none">
        <Canvas camera={{ position: [0, 0, 1] }}>
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        </Canvas>
    </div>
);

const Navbar = () => (
    <nav className="flex justify-between items-center px-8 py-4 border-b border-slate-800 bg-slate-950/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-8">
            <h1 className="text-xl font-extrabold text-blue-500 tracking-tighter">FIN-GUARD</h1>
            <SignedIn>
                <div className="hidden md:flex gap-6 text-sm font-medium text-slate-400">
                    <a href="/dashboard" className="hover:text-white transition">Dashboard</a>
                    <a href="/decisions" className="hover:text-white transition">Risk Engine</a>
                    <a href="/chat" className="hover:text-white transition">AI Assistant</a>
                </div>
            </SignedIn>
        </div>
        <div className="flex items-center gap-4">
            <SignedIn>
                <UserButton afterSignOutUrl="/" />
            </SignedIn>
            <SignedOut>
                <a href="/" className="text-sm font-semibold hover:text-blue-400">Log In</a>
            </SignedOut>
        </div>
    </nav>
);

function App() {
    return (
        <div className="min-h-screen text-slate-200">
            <SceneBg />
            <Navbar />

            <main className="relative z-10">
                <Routes>
                    {/* Public Route */}
                    <Route path="/" element={<Landing />} />

                    {/* Protected Routes */}
                    <Route
                        path="/dashboard"
                        element={
                            <SignedIn>
                                <Dashboard />
                            </SignedIn>
                        }
                    />
                    <Route
                        path="/decisions"
                        element={
                            <SignedIn>
                                <Decisions />
                            </SignedIn>
                        }
                    />
                    <Route
                        path="/chat"
                        element={
                            <SignedIn>
                                <Chat />
                            </SignedIn>
                        }
                    />

                    {/* Fallback */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </main>

            <footer className="py-10 text-center text-slate-600 text-xs">
                © 2026 FinGuard AI. Designed for Financial Stability.
            </footer>
        </div>
    );
}

export default App;