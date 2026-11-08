"use client";

import { createContext, useCallback, useContext, useState } from "react";
import clsx from "clsx";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";

type ToastType = "success" | "error" | "info" | "warning";

interface Toast {
  id: string;
  message: string;
  type: ToastType;
}

interface ToastContextType {
  toast: (message: string, type?: ToastType) => void;
}

const ToastContext = createContext<ToastContextType>({ toast: () => {} });

export function useToast() { return useContext(ToastContext); }

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: ToastType = "info") => {
    const id = Math.random().toString(36).slice(2);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000);
  }, []);

  const remove = (id: string) => setToasts((prev) => prev.filter((t) => t.id !== id));

  const icons = {
    success: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
    error: <AlertCircle className="w-4 h-4 text-red-400" />,
    warning: <AlertCircle className="w-4 h-4 text-amber-400" />,
    info: <Info className="w-4 h-4 text-cyan-400" />,
  };

  const styles = {
    success: "border-emerald-500/20 bg-emerald-500/5",
    error: "border-red-500/20 bg-red-500/5",
    warning: "border-amber-500/20 bg-amber-500/5",
    info: "border-cyan-500/20 bg-cyan-500/5",
  };

  return (
    <ToastContext.Provider value={{ toast: addToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
        {toasts.map((t) => (
          <div key={t.id} className={clsx("flex items-start gap-2 p-3 rounded-lg border shadow-xl shadow-black/20 backdrop-blur-sm bg-[#0F172A] animate-slide-in", styles[t.type])}>
            {icons[t.type]}
            <span className="text-sm text-slate-200 flex-1">{t.message}</span>
            <button onClick={() => remove(t.id)} className="text-slate-500 hover:text-slate-300">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
