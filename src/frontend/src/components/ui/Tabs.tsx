import { useState } from "react";

interface Tab {
  key: string;
  label: string;
}

interface TabsProps {
  tabs: Tab[];
  defaultTab?: string;
  activeTab?: string;
  onTabChange?: (key: string) => void;
  children: (activeTab: string) => React.ReactNode;
}

/** Reusable tabs component with controlled or uncontrolled mode. */
export default function Tabs({ tabs, defaultTab, activeTab, onTabChange, children }: TabsProps) {
  const [internalTab, setInternalTab] = useState(defaultTab ?? tabs[0]?.key ?? "");
  const current = activeTab ?? internalTab;

  const handleClick = (key: string) => {
    if (!activeTab) setInternalTab(key);
    onTabChange?.(key);
  };

  return (
    <div>
      <div className="flex border-b border-gray-200 mb-3 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => handleClick(tab.key)}
            className={`px-3 py-1.5 text-sm font-medium border-b-2 transition-colors whitespace-nowrap shrink-0 ${
              current === tab.key
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
      {children(current)}
    </div>
  );
}
