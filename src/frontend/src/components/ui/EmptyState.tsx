interface EmptyStateProps {
  message: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export default function EmptyState({ message, action }: EmptyStateProps) {
  return (
    <div className="text-center py-12">
      <p className="text-gray-400 text-sm">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="mt-3 text-sm text-blue-600 hover:underline"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
