import { Component } from "react";
import type { ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallbackMessage?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Catches render-time exceptions in its subtree and shows a
 * recovery UI instead of blanking the page.
 */
export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <p className="text-red-600 font-medium mb-2">
            {this.props.fallbackMessage ?? "Something went wrong."}
          </p>
          <p className="text-sm text-gray-500 mb-4 max-w-md">
            {this.state.error?.message}
          </p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
