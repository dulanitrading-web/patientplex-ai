"use client";

import React from "react";

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log to console in development, send to error tracking in production
    console.error("[PatientPlex Error]", error, errorInfo);

    // TODO: Send to Sentry or similar when configured
    // if (process.env.NEXT_PUBLIC_SENTRY_DSN) {
    //   Sentry.captureException(error, { extra: errorInfo });
    // }
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="min-h-[400px] flex items-center justify-center p-8">
            <div className="text-center max-w-md">
              <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-50 flex items-center justify-center">
                <svg className="w-8 h-8 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Something went wrong</h3>
              <p className="text-sm text-slate-500 mb-4">
                We encountered an unexpected error. Please try refreshing the page.
              </p>
              <button
                onClick={() => this.setState({ hasError: false })}
                className="px-4 py-2 bg-emerald-500 text-white rounded-lg text-sm font-semibold hover:bg-emerald-600 transition-colors"
              >
                Try again
              </button>
            </div>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
