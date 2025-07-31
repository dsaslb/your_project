'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({ error, errorInfo });
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-6">
          <Card className="w-full max-w-md bg-slate-800/50 border-red-500/30 backdrop-blur-xl">
            <CardHeader className="text-center">
              <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
              <CardTitle className="text-red-400">오류가 발생했습니다</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-slate-300 text-sm text-center">
                예상치 못한 오류가 발생했습니다. 다시 시도해주세요.
              </p>
              
              {process.env.NODE_ENV === 'development' && this.state.error && (
                <details className="text-xs text-slate-400">
                  <summary className="cursor-pointer hover:text-slate-300">
                    개발자 정보 (클릭하여 확장)
                  </summary>
                  <div className="mt-2 p-2 bg-slate-900/50 rounded border border-slate-600">
                    <p className="font-mono break-all">
                      {this.state.error.message}
                    </p>
                    {this.state.errorInfo && (
                      <pre className="mt-2 text-xs overflow-auto">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    )}
                  </div>
                </details>
              )}

              <div className="flex gap-3">
                <Button
                  onClick={this.handleRetry}
                  className="flex-1 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border-cyan-500/30 hover:from-cyan-500/30 hover:to-purple-500/30"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  다시 시도
                </Button>
                <Button
                  onClick={this.handleGoHome}
                  variant="outline"
                  className="flex-1 border-slate-600 text-slate-300 hover:bg-slate-700"
                >
                  <Home className="w-4 h-4 mr-2" />
                  홈으로
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary; 