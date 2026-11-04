"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try { return localStorage.getItem("pp_token"); } catch { return null; }
}

/** Authenticated fetch wrapper */
export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const msg = (body as Record<string, string>).detail || res.statusText || "Request failed";
    throw new Error(msg);
  }

  return res.json() as Promise<T>;
}

/** React hook for GET requests with caching, loading, and error states */
export function useQuery<T = unknown>(path: string | null, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(!!path);
  const [error, setError] = useState<string | null>(null);
  const mounted = useRef(true);

  const refetch = useCallback(async () => {
    if (!path) return;
    setLoading(true);
    setError(null);
    try {
      const result = await apiFetch<T>(path);
      if (mounted.current) setData(result);
    } catch (err) {
      if (mounted.current) setError(err instanceof Error ? err.message : "Failed");
    } finally {
      if (mounted.current) setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    mounted.current = true;
    refetch();
    return () => { mounted.current = false; };
  }, [refetch, ...deps]);

  return { data, loading, error, refetch };
}

/** React hook for POST/PUT/DELETE mutations */
export function useMutation<T = unknown, V = unknown>(
  path: string,
  method: "POST" | "PUT" | "DELETE" = "POST",
) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const mutate = useCallback(async (body?: V): Promise<T> => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFetch<T>(path, {
        method,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });
      return result;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed";
      setError(msg);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [path, method]);

  return { mutate, loading, error };
}
