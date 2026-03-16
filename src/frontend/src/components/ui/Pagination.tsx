interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export default function Pagination({
  page,
  totalPages,
  onPageChange,
}: PaginationProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-between mt-4 text-sm">
      <button
        disabled={page === 0}
        onClick={() => onPageChange(Math.max(0, page - 1))}
        className="px-3 py-1 border border-gray-300 rounded disabled:opacity-40 hover:bg-gray-100"
      >
        Previous
      </button>
      <span className="text-gray-500">
        Page {page + 1} of {totalPages}
      </span>
      <button
        disabled={page >= totalPages - 1}
        onClick={() => onPageChange(Math.min(totalPages - 1, page + 1))}
        className="px-3 py-1 border border-gray-300 rounded disabled:opacity-40 hover:bg-gray-100"
      >
        Next
      </button>
    </div>
  );
}
