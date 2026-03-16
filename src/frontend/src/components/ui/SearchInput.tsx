import { useDebounce } from "../../hooks/useDebounce";
import { useState, useEffect } from "react";

interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  debounceMs?: number;
  className?: string;
}

export default function SearchInput({
  value,
  onChange,
  placeholder = "Search...",
  debounceMs = 300,
  className = "",
}: SearchInputProps) {
  const [local, setLocal] = useState(value);
  const debounced = useDebounce(local, debounceMs);

  // Sync external value changes
  useEffect(() => {
    setLocal(value);
  }, [value]);

  // Emit debounced value
  useEffect(() => {
    if (debounced !== value) {
      onChange(debounced);
    }
  }, [debounced, onChange, value]);

  return (
    <div className={`relative ${className}`}>
      <input
        type="text"
        value={local}
        onChange={(e) => setLocal(e.target.value)}
        placeholder={placeholder}
        className="w-full text-sm border border-gray-300 rounded px-3 py-1.5 pr-8 focus:outline-none focus:ring-1 focus:ring-blue-300 focus:border-blue-300"
      />
      {local && (
        <button
          onClick={() => {
            setLocal("");
            onChange("");
          }}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 text-sm"
          aria-label="Clear search"
        >
          x
        </button>
      )}
    </div>
  );
}
