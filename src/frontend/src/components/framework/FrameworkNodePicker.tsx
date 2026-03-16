import { useState, useRef, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../utils/api";
import type { FrameworkNode } from "../../types/framework";
import { useDebounce } from "../../hooks/useDebounce";

interface FlatNode {
  id: number;
  label: string;
  depth: number;
}

function flattenTree(nodes: FrameworkNode[], parentPath?: string): FlatNode[] {
  const result: FlatNode[] = [];
  for (const node of nodes) {
    const label = parentPath ? `${parentPath} > ${node.title}` : node.title;
    result.push({ id: node.id, label, depth: node.depth });
    if (node.children.length > 0) {
      result.push(...flattenTree(node.children, label));
    }
  }
  return result;
}

interface FrameworkNodePickerProps {
  value: number | null;
  onChange: (nodeId: number | null) => void;
  placeholder?: string;
  disabled?: boolean;
}

export default function FrameworkNodePicker({
  value,
  onChange,
  placeholder = "Select a topic...",
  disabled = false,
}: FrameworkNodePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 200);
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const { data: tree, isLoading } = useQuery({
    queryKey: ["framework", "tree", "picker"],
    queryFn: () =>
      api.get<FrameworkNode[]>("/framework/tree", {
        params: { max_depth: 2 },
      }),
    staleTime: 5 * 60 * 1000,
  });

  const flatNodes = useMemo(() => (tree ? flattenTree(tree) : []), [tree]);

  const filtered = useMemo(() => {
    if (!debouncedSearch) return flatNodes;
    const lower = debouncedSearch.toLowerCase();
    return flatNodes.filter((n) => n.label.toLowerCase().includes(lower));
  }, [flatNodes, debouncedSearch]);

  const selectedLabel = useMemo(() => {
    if (value === null) return "";
    return flatNodes.find((n) => n.id === value)?.label ?? "";
  }, [value, flatNodes]);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
        setSearch("");
      }
    }
    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
      return () =>
        document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [isOpen]);

  function handleSelect(node: FlatNode) {
    onChange(node.id);
    setIsOpen(false);
    setSearch("");
  }

  function handleClear(e: React.MouseEvent) {
    e.stopPropagation();
    onChange(null);
    setSearch("");
  }

  function handleInputClick() {
    if (!disabled) {
      setIsOpen(true);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Escape") {
      setIsOpen(false);
      setSearch("");
    }
  }

  return (
    <div ref={containerRef} className="relative" onKeyDown={handleKeyDown}>
      {/* Trigger / display area */}
      <div
        onClick={handleInputClick}
        className={`flex items-center border rounded px-2 py-1.5 text-sm cursor-pointer ${
          disabled
            ? "bg-gray-100 text-gray-400 cursor-not-allowed"
            : "border-gray-300 bg-white hover:border-gray-400"
        } ${isOpen ? "ring-1 ring-blue-300 border-blue-300" : ""}`}
      >
        {isOpen ? (
          <input
            ref={inputRef}
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={selectedLabel || placeholder}
            className="flex-1 outline-none bg-transparent text-gray-700 placeholder-gray-400"
          />
        ) : (
          <span
            className={`flex-1 truncate ${value ? "text-gray-700" : "text-gray-400"}`}
          >
            {selectedLabel || placeholder}
          </span>
        )}

        {value !== null && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="ml-1 text-gray-400 hover:text-gray-600 shrink-0"
            title="Clear selection"
          >
            x
          </button>
        )}

        <svg
          className={`ml-1 w-4 h-4 text-gray-400 shrink-0 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 mt-1 w-full max-h-60 overflow-auto bg-white border border-gray-200 rounded shadow-lg">
          {isLoading && (
            <div className="px-3 py-2 text-sm text-gray-400">Loading...</div>
          )}

          {!isLoading && filtered.length === 0 && (
            <div className="px-3 py-2 text-sm text-gray-400">
              No topics found
            </div>
          )}

          {filtered.map((node) => (
            <button
              type="button"
              key={node.id}
              onClick={() => handleSelect(node)}
              className={`w-full text-left px-3 py-1.5 text-sm hover:bg-blue-50 ${
                node.id === value
                  ? "bg-blue-50 text-blue-700 font-medium"
                  : "text-gray-700"
              }`}
              style={{ paddingLeft: `${node.depth * 16 + 12}px` }}
            >
              {node.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
