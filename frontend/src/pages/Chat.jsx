import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { useApi } from '../services/api';
import { Send } from 'lucide-react';

const Chat = () => {
    const [messages, setMessages] = useState([{ role: 'ai', content: 'Hello! I can explain the risks of your financial decisions. How can I help?' }]);
    const [input, setInput] = useState('');
    const { getToken } = useAuth();
    const api = useApi(getToken);
    const scrollRef = useRef();

    useEffect(() => { scrollRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

    const onSend = async () => {
        if (!input.trim()) return;
        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');

        try {
            const res = await api.sendMessage(input);
            setMessages(prev => [...prev, { role: 'ai', content: res.data.reply }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'ai', content: 'Sorry, I’m having trouble connecting to the metrics engine.' }]);
        }
    };

    return (
        <div className="flex flex-col h-[80vh] max-w-3xl mx-auto bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden mt-10">
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.map((m, i) => (
                    <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] p-4 rounded-2xl ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-200'}`}>
                            {m.content}
                        </div>
                    </div>
                ))}
                <div ref={scrollRef} />
            </div>
            <div className="p-4 bg-slate-950 flex gap-2">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && onSend()}
                    placeholder="Ask about your financial safety..."
                    className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-white outline-none focus:border-blue-500"
                />
                <button onClick={onSend} className="p-3 bg-blue-600 rounded-xl hover:bg-blue-700 transition">
                    <Send size={20} />
                </button>
            </div>
        </div>
    );
};
export default Chat;