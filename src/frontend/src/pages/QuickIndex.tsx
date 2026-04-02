import { Link } from "react-router-dom";

const problems: { dbId: number; lcId?: number; title: string }[] = [
  { dbId: 93, lcId: 146, title: "LRU Cache" },
  { dbId: 179, lcId: 716, title: "Max Stack" },
  { dbId: 182, lcId: 432, title: "All O`one Data Structure" },
  { dbId: 99, lcId: 215, title: "Kth Largest Element in an Array" },
  { dbId: 115, lcId: 127, title: "Word Ladder" },
  { dbId: 510, lcId: 373, title: "Find K Pairs with Smallest Sums" },
  { dbId: 29, lcId: 235, title: "Lowest Common Ancestor of a BST" },
  { dbId: 38, lcId: 212, title: "Word Search II" },
  { dbId: 48, lcId: 269, title: "Alien Dictionary" },
  { dbId: 10, lcId: 15, title: "3Sum" },
  { dbId: 42, lcId: 200, title: "Number of Islands" },
  { dbId: 1064, title: "K-Means (K-Means++)" },
  { dbId: 1050, title: "Lock Combination BFS (Bidirectional)" },
  { dbId: 805, lcId: 2503, title: "Max Points From Grid Queries" },
  { dbId: 216, lcId: 2791, title: "Palindrome Paths in Tree" },
  { dbId: 183, lcId: 2858, title: "Min Edge Reversals" },
];

export default function QuickIndex() {
  return (
    <div className="p-6 h-full overflow-y-auto">
      <h1 className="text-2xl font-bold mb-6">Quick Index</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {problems.map((p) => (
          <Link
            key={p.dbId}
            to={`/problems/${p.dbId}`}
            className="block p-4 rounded-lg border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all bg-white"
          >
            <span className="text-xs text-gray-400 font-mono">
              {p.lcId ? `#${p.lcId}` : "Custom"}
            </span>
            <div className="mt-1 font-medium text-gray-800">{p.title}</div>
          </Link>
        ))}
      </div>
    </div>
  );
}
