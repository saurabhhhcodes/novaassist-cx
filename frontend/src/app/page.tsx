"use client";

import { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Paperclip, Mic, Ticket, Loader2 } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Helper for tailwind class merging
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8002";

interface Message {
  role: 'user' | 'assistant';
  content: string;
  ticketId?: string;
  image?: string;
}

const MessageContent = ({ content }: { content: string }) => {
  const thinkingMatch = content.match(/<thinking>([\s\S]*?)<\/thinking>/);
  const thinking = thinkingMatch ? thinkingMatch[1].trim() : null;
  const mainContent = content.replace(/<thinking>[\s\S]*?<\/thinking>/, "").trim();

  return (
    <div className="space-y-3">
      {thinking && (
        <div className="bg-purple-500/5 border border-purple-500/10 rounded-xl p-3 text-[11px] text-purple-300 italic mb-2 relative overflow-hidden group/think">
          <div className="flex items-center gap-2 mb-1 text-purple-400 font-bold uppercase tracking-tighter">
             <div className="w-1.5 h-1.5 rounded-full bg-purple-500 animate-pulse" />
             Internal Reasoning
          </div>
          {thinking}
        </div>
      )}
      {mainContent.split('\n').map((line, i) => <p key={i}>{line}</p>)}
    </div>
  );
};

export default function NovaAssistApp() {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hello! I'm NovaAssist CX. I've analyzed your recent history and I'm ready to resolve your logistics, billing, or technical issues autonomously. How can I help you today?" }
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [email] = useState("saurabh@exclusive.com");
  const [isRecording, setIsRecording] = useState(false);
  const [transcriptionStatus, setTranscriptionStatus] = useState<string | null>(null);
  const [impactMetrics] = useState({ savedHours: 156, efficiency: 91 });
  
  const scrollRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const stopPlayback = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    stopPlayback();

    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/support/chat`, {
        message: input,
        customer_email: email,
        session_id: sessionId
      });

      if (response.data.session_id) {
        setSessionId(response.data.session_id);
      }

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response
      }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Backend Error: Please verify server is listening on 8002." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    stopPlayback();

    const formData = new FormData();
    formData.append("file", file);
    formData.append("email", email);

    setIsLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: "Uploaded a screenshot for Nova Vision analysis..." }]);

    try {
      const response = await axios.post(`${API_BASE}/support/upload`, formData);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Vision Analysis: ${response.data.analysis}`,
        ticketId: response.data.ticket_id
      }]);
    } catch (error: any) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Analysis Failed. Check AWS Bedrock permissions." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const toggleRecording = async () => {
    stopPlayback();
    if (isRecording) {
      setIsRecording(false);
      mediaRecorderRef.current?.stop();
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) audioChunksRef.current.push(event.data);
        };

        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          setIsLoading(true);
          setTranscriptionStatus("Transcribing...");
          setMessages(prev => [...prev, { role: 'user', content: "🎤 [Neural Voice Command]" }]);

          try {
            const formData = new FormData();
            formData.append("file", audioBlob, "voice.webm");
            formData.append("email", email);
            if (sessionId) formData.append("session_id", sessionId);

            setTranscriptionStatus("Nova is thinking...");
            const response = await axios.post(`${API_BASE}/support/voice`, formData);
            
            if (response.data.session_id) setSessionId(response.data.session_id);

            setMessages(prev => [...prev, { 
              role: 'assistant', 
              content: response.data.response 
            }]);

            if (response.data.audio) {
              setTranscriptionStatus("Synthesis...");
              const audio = new Audio(`data:audio/mp3;base64,${response.data.audio}`);
              audioRef.current = audio;
              audio.play();
            }
          } catch (error) {
            console.error(error);
          } finally {
            setIsLoading(false);
            setTranscriptionStatus(null);
          }
          stream.getTracks().forEach(track => track.stop());
        };

        mediaRecorder.start();
        setIsRecording(true);
      } catch (err) {
        console.error("Mic access failed:", err);
      }
    }
  };

  return (
    <main className="min-h-screen bg-mesh flex flex-col items-center p-4 md:p-8 custom-scrollbar">
      {/* Header & Branding */}
      <div className="w-full max-w-6xl flex flex-col md:flex-row justify-between items-center mb-12 gap-6 pt-4">
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col"
        >
          <h1 className="text-4xl md:text-6xl font-black tracking-tighter text-white flex items-center gap-3">
            NOVA<span className="text-blue-500 font-black">ASSIST</span> CX
          </h1>
          <div className="flex items-center gap-4">
            <p className="text-zinc-500 font-semibold tracking-tight">Enterprise Agentic Intelligence • Amazon Nova AI Hackathon</p>
            <button 
              onClick={() => {
                const audio = new Audio('/intro.mp3');
                audio.play();
              }}
              className="text-[10px] bg-blue-500/10 text-blue-400 px-3 py-1 rounded-full border border-blue-500/20 font-bold hover:bg-blue-500/20 transition-all active:scale-95"
            >
              PLAY INTRO
            </button>
          </div>
        </motion.div>

        {/* Impact Dashboard */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="grid grid-cols-2 gap-4 w-full md:w-auto"
        >
          <div className="dashboard-card flex flex-col items-center justify-center min-w-[150px] py-4 bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-3xl">
            <span className="text-3xl font-black text-blue-400">{impactMetrics.savedHours}h</span>
            <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-bold">Hours Saved</span>
          </div>
          <div className="dashboard-card flex flex-col items-center justify-center min-w-[150px] py-4 bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-3xl">
            <span className="text-3xl font-black text-purple-400">{impactMetrics.efficiency}%</span>
            <span className="text-[10px] uppercase tracking-[0.2em] text-zinc-500 font-bold">Agency Score</span>
          </div>
        </motion.div>
      </div>

      <div className="w-full max-w-6xl grid grid-cols-1 lg:grid-cols-4 gap-8 flex-1">
        {/* Chat Area */}
        <div className="lg:col-span-3 flex flex-col h-[70vh] glass-premium rounded-[2.5rem] overflow-hidden relative border border-white/5 shadow-2xl">
          <div ref={scrollRef} className="flex-1 p-6 overflow-y-auto space-y-6 custom-scrollbar">
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
                animate={{ opacity: 1, x: 0 }}
                className={cn("flex gap-4", msg.role === 'user' ? "flex-row-reverse" : "")}
              >
                <div className={cn(
                  "w-10 h-10 rounded-2xl flex items-center justify-center shrink-0 shadow-lg",
                  msg.role === 'user' ? "bg-blue-600" : "bg-gradient-to-br from-zinc-800 to-zinc-900 border border-white/5"
                )}>
                  {msg.role === 'user' ? <User size={20} /> : <Bot size={21} className="text-blue-400" />}
                </div>
                <div className={cn(
                  "max-w-[80%] p-4 rounded-3xl text-sm leading-relaxed",
                  msg.role === 'user' ? "bg-blue-600/10 text-white rounded-tr-none border border-blue-500/20" : "bg-white/5 text-zinc-200 rounded-tl-none border border-white/5 shadow-xl"
                )}>
                  <MessageContent content={msg.content} />
                  {msg.ticketId && (
                    <div className="mt-3 flex items-center gap-2 px-3 py-1.5 bg-green-500/20 text-green-400 rounded-full text-[10px] font-bold border border-green-500/30">
                      <Ticket size={12} /> TICKET: {msg.ticketId}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            {isLoading && (
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-2xl bg-zinc-800 flex items-center justify-center animate-pulse border border-white/5">
                  <Bot size={21} className="text-zinc-500" />
                </div>
                <div className="bg-white/5 p-4 rounded-3xl rounded-tl-none border border-white/5 flex items-center gap-3">
                  <Loader2 size={14} className="animate-spin text-blue-500" />
                  <span className="text-xs text-zinc-400 font-medium italic">
                    {transcriptionStatus || "Nova is reasoning..."}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div className="p-6 bg-white/[0.02] border-t border-white/[0.05]">
            <div className="relative group">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                placeholder="Talk to Nova... (e.g. 'Redirect order ORD-777')"
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-6 pr-40 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-zinc-600"
              />
              <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-2 px-2">
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 hover:bg-white/10 rounded-xl transition-all text-zinc-400 hover:text-white"
                >
                  <Paperclip size={20} />
                </button>
                <button
                  onClick={toggleRecording}
                  className={cn(
                    "p-3 rounded-xl transition-all shadow-lg scale-95 hover:scale-100",
                    isRecording ? "bg-red-500 text-white animate-pulse" : "bg-blue-600 text-white hover:bg-blue-500"
                  )}
                >
                   {isRecording ? <Mic size={20} className="animate-bounce" /> : <Mic size={20} />}
                </button>
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="p-2 text-blue-500 hover:scale-110 transition-all disabled:text-zinc-700"
                >
                  <Send size={24} strokeWidth={2.5} />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Features */}
        <div className="space-y-6 lg:block hidden">
          <div className="dashboard-card bg-gradient-to-br from-blue-600/10 to-transparent border border-blue-500/10 backdrop-blur-xl">
             <h3 className="text-white font-bold mb-3 flex items-center gap-2 text-sm">
               <div className="w-2 h-2 rounded-full bg-blue-500" />
               Enterprise IQ
             </h3>
             <p className="text-[11px] text-zinc-400 leading-relaxed font-medium">
               Nova connects directly to enterprise SQLite/PostgreSQL databases for real-world persistence.
             </p>
          </div>

          <div className="dashboard-card bg-gradient-to-br from-purple-600/10 to-transparent border border-purple-500/10 backdrop-blur-xl">
             <h3 className="text-white font-bold mb-3 flex items-center gap-2 text-sm">
               <div className="w-2 h-2 rounded-full bg-purple-500" />
               Multimodal Vision
             </h3>
             <p className="text-[11px] text-zinc-400 leading-relaxed font-medium">
               Real-time visual analysis of technical setup via **Nova 2 Lite**.
             </p>
          </div>

          <div className="flex flex-col items-center justify-center p-8 mt-6 opacity-40 hover:opacity-100 transition-all duration-700 group cursor-default">
             <Bot size={64} className="text-blue-500 mb-6 group-hover:scale-110 transition-transform duration-500" />
             <span className="text-xs font-black uppercase tracking-[0.5em] text-white">SAURABH KUMAR BAJPAI</span>
             <span className="text-[9px] text-zinc-600 font-bold uppercase mt-3 tracking-[0.2em]">Amazon Nova AI Hackathon Submission</span>
          </div>
        </div>
      </div>

      <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept="image/*" />
    </main>
  );
}
