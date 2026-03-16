import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../../utils/api";
import { useToast } from "../../contexts/ToastContext";
import FrameworkNodePicker from "../framework/FrameworkNodePicker";
import ConfirmDialog from "../ui/ConfirmDialog";
import type { TopicWeight } from "../../types/company";

interface TopicWeightEditorProps {
  companyId: number;
}

export default function TopicWeightEditor({
  companyId,
}: TopicWeightEditorProps) {
  const queryClient = useQueryClient();
  const toast = useToast();

  // Fetch current weights via company detail endpoint
  const { data: companyDetail, isLoading } = useQuery({
    queryKey: ["companies", companyId, "detail"],
    queryFn: () =>
      api.get<{ topic_weights: TopicWeight[] }>(`/companies/${companyId}`),
  });

  const weights = companyDetail?.topic_weights ?? [];

  // Local state for editing weight values
  const [editedWeights, setEditedWeights] = useState<
    Record<number, number>
  >({});
  const [addNodeId, setAddNodeId] = useState<number | null>(null);
  const [addWeight, setAddWeight] = useState(1);
  const [deleteTarget, setDeleteTarget] = useState<TopicWeight | null>(null);

  // Upsert mutation (for updating slider values and adding new weights)
  const upsertMutation = useMutation({
    mutationFn: (payload: { framework_node_id: number; weight: number }[]) =>
      api.post(`/companies/${companyId}/weights`, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["companies", companyId],
      });
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      setEditedWeights({});
      toast.success("Weights updated");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to update weights");
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (nodeId: number) =>
      api.del(`/companies/${companyId}/weights/${nodeId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["companies", companyId],
      });
      queryClient.invalidateQueries({ queryKey: ["companies"] });
      setDeleteTarget(null);
      toast.success("Topic weight removed");
    },
    onError: (err: Error) => {
      toast.error(err.message || "Failed to remove weight");
      setDeleteTarget(null);
    },
  });

  function handleSliderChange(nodeId: number, value: number) {
    setEditedWeights((prev) => ({ ...prev, [nodeId]: value }));
  }

  function handleSaveWeights() {
    const changes = Object.entries(editedWeights).map(([nodeId, weight]) => ({
      framework_node_id: Number(nodeId),
      weight,
    }));
    if (changes.length > 0) {
      upsertMutation.mutate(changes);
    }
  }

  function handleAddWeight() {
    if (addNodeId === null) return;
    upsertMutation.mutate([
      { framework_node_id: addNodeId, weight: addWeight },
    ]);
    setAddNodeId(null);
    setAddWeight(1);
  }

  const hasChanges = Object.keys(editedWeights).length > 0;
  const existingNodeIds = new Set(weights.map((w) => w.node_id));

  if (isLoading) {
    return (
      <div className="text-sm text-gray-400 py-2 text-center">
        Loading weights...
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700">Topic Weights</h3>
        {hasChanges && (
          <button
            onClick={handleSaveWeights}
            disabled={upsertMutation.isPending}
            className="text-xs px-2 py-0.5 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {upsertMutation.isPending ? "..." : "Save Changes"}
          </button>
        )}
      </div>

      {/* Current weights list with sliders */}
      {weights.length === 0 && (
        <div className="text-xs text-gray-400 text-center py-2">
          No topic weights assigned.
        </div>
      )}

      {weights.map((w) => {
        const currentValue =
          editedWeights[w.node_id] !== undefined
            ? editedWeights[w.node_id]
            : w.weight;
        return (
          <div
            key={w.node_id}
            className="border border-gray-200 rounded p-2 space-y-1"
          >
            <div className="flex items-center justify-between gap-1">
              <span className="text-sm font-medium truncate flex-1">
                {w.node_title}
              </span>
              <span className="text-xs text-gray-500 shrink-0 w-8 text-right">
                {currentValue.toFixed(1)}
              </span>
              <button
                type="button"
                onClick={() => setDeleteTarget(w)}
                className="text-gray-400 hover:text-red-500 text-xs shrink-0 ml-1"
                title="Remove topic weight"
              >
                x
              </button>
            </div>
            <input
              type="range"
              min={0}
              max={5}
              step={0.5}
              value={currentValue}
              onChange={(e) =>
                handleSliderChange(w.node_id, parseFloat(e.target.value))
              }
              className="w-full h-1.5 accent-blue-500"
            />
          </div>
        );
      })}

      {/* Add new weight */}
      <div className="border border-dashed border-gray-300 rounded p-2 space-y-2">
        <div className="text-xs font-medium text-gray-500">Add topic</div>
        <FrameworkNodePicker
          value={addNodeId}
          onChange={(id) => {
            // Prevent selecting nodes that already have weights
            if (id !== null && existingNodeIds.has(id)) {
              toast.info("This topic already has a weight assigned.");
              return;
            }
            setAddNodeId(id);
          }}
          placeholder="Select a topic to add..."
        />
        {addNodeId !== null && (
          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-500">Weight:</label>
            <input
              type="range"
              min={0}
              max={5}
              step={0.5}
              value={addWeight}
              onChange={(e) => setAddWeight(parseFloat(e.target.value))}
              className="flex-1 h-1.5 accent-blue-500"
            />
            <span className="text-xs text-gray-500 w-6 text-right">
              {addWeight.toFixed(1)}
            </span>
            <button
              onClick={handleAddWeight}
              disabled={upsertMutation.isPending}
              className="text-xs px-2 py-0.5 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              Add
            </button>
          </div>
        )}
      </div>

      {/* Delete confirmation */}
      <ConfirmDialog
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() =>
          deleteTarget && deleteMutation.mutate(deleteTarget.node_id)
        }
        title="Remove Topic Weight"
        message={`Remove weight for "${deleteTarget?.node_title ?? ""}" from this company?`}
        confirmLabel="Remove"
        confirmVariant="danger"
        loading={deleteMutation.isPending}
      />
    </div>
  );
}
