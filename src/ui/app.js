const { useState, useEffect, useRef } = React;

function NanikaChat() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [intent, setIntent] = useState("chat");
    
    const sendMessage = async () => {
        if (!input.trim() || loading) return;
        
        // Add user message
        const userMsg = { role: "you", text: input, at: new Date().toISOString() };
        setMessages(prev => [...prev, userMsg]);
        
        // Clear input
        const instruction = input;
        setInput("");
        setLoading(true);
        
        try {
            // Send to API
            const response = await fetch("/task", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    intent: intent,
                    instruction: intent === "chat" ? `respond to: ${instruction}` : instruction,
                    context: {}
                })
            });
            
            if (!response.ok) throw new Error("Failed to send");
            
            // Wait a bit then check for response
            setTimeout(async () => {
                try {
                    const latest = await fetch("/latest");
                    const data = await latest.json();
                    if (data.text) {
                        setMessages(prev => [...prev, {
                            role: "nanika",
                            text: data.text,
                            at: new Date().toISOString()
                        }]);
                    }
                } catch (e) {
                    console.error("Error getting response:", e);
                }
                setLoading(false);
            }, 3000);
            
        } catch (error) {
            console.error("Error:", error);
            setLoading(false);
        }
    };
    
    return (
        <div className="min-h-screen bg-gray-950 text-gray-200 flex flex-col">
            {/* Header */}
            <header className="border-b border-gray-800 p-4">
                <div className="max-w-4xl mx-auto flex items-center justify-between">
                    <h1 className="text-xl font-mono">nanika</h1>
                    <div className="flex gap-4 text-sm">
                        <select 
                            value={intent} 
                            onChange={e => setIntent(e.target.value)}
                            className="bg-gray-900 border border-gray-800 rounded px-2 py-1"
                        >
                            <option value="chat">chat</option>
                            <option value="plan">plan</option>
                            <option value="research">research</option>
                            <option value="build">build</option>
                        </select>
                    </div>
                </div>
            </header>
            
            {/* Messages */}
            <div className="flex-1 max-w-4xl mx-auto w-full p-4 space-y-4 overflow-auto">
                {messages.map((msg, i) => (
                    <div key={i} className={`p-4 rounded-lg ${
                        msg.role === "you" ? "bg-gray-900" : "bg-purple-950/30 border border-purple-900/50"
                    }`}>
                        <div className="text-xs text-gray-500 mb-1">{msg.role}</div>
                        <div className="whitespace-pre-wrap">{msg.text}</div>
                    </div>
                ))}
                {loading && (
                    <div className="text-gray-500 text-sm">nanika is thinking...</div>
                )}
            </div>
            
            {/* Input */}
            <div className="border-t border-gray-800 p-4">
                <div className="max-w-4xl mx-auto flex gap-2">
                    <textarea
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        onKeyDown={e => {
                            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                                sendMessage();
                            }
                        }}
                        placeholder="speak to nanika... (Ctrl+Enter to send)"
                        className="flex-1 bg-gray-900 border border-gray-800 rounded-lg p-3 resize-none"
                        rows={3}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading || !input.trim()}
                        className="px-6 py-3 bg-purple-900 hover:bg-purple-800 disabled:bg-gray-800 rounded-lg"
                    >
                        send
                    </button>
                </div>
            </div>
        </div>
    );
}

// Render the app
ReactDOM.render(<NanikaChat />, document.getElementById("root"));
