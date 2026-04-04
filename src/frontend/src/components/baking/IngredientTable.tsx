import type { BakingIngredient } from "../../types/baking";

interface IngredientTableProps {
  ingredients: BakingIngredient[];
  scaledAmounts?: Record<number, number>;
}

export default function IngredientTable({
  ingredients,
  scaledAmounts,
}: IngredientTableProps) {
  // Group ingredients by group_name
  const groups = new Map<string, BakingIngredient[]>();
  for (const ing of ingredients) {
    const key = ing.group_name || "main";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)!.push(ing);
  }

  const GROUP_LABELS: Record<string, string> = {
    main: "Main",
    topping: "Topping",
    frosting: "Frosting",
    filling: "Filling",
    yolk_batter: "Yolk Batter",
    meringue: "Meringue",
  };

  return (
    <div className="space-y-3">
      {[...groups.entries()].map(([groupName, items]) => (
        <div key={groupName}>
          {groups.size > 1 && (
            <h4 className="text-xs font-semibold text-amber-700 uppercase tracking-wide mb-1">
              {GROUP_LABELS[groupName] ?? groupName}
            </h4>
          )}
          <table className="w-full text-sm">
            <tbody>
              {items.map((ing) => {
                const amount = scaledAmounts?.[ing.id] ?? ing.amount;
                return (
                  <tr
                    key={ing.id}
                    className="border-b border-amber-50 last:border-0"
                  >
                    <td className="py-1.5 text-gray-800">
                      {ing.name_zh ? (
                        <span>
                          {ing.name_zh}{" "}
                          <span className="text-gray-400 text-xs">
                            {ing.name}
                          </span>
                        </span>
                      ) : (
                        ing.name
                      )}
                    </td>
                    <td className="py-1.5 text-right font-mono text-gray-700 whitespace-nowrap">
                      {amount > 0 ? (
                        <>
                          {amount}
                          <span className="text-gray-400 ml-0.5">
                            {ing.unit}
                          </span>
                        </>
                      ) : (
                        <span className="text-gray-400">{ing.unit}</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  );
}
