import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import Modal from "../ui/Modal";
import PrepNotesTab from "../companies/PrepNotesTab";
import { api } from "../../utils/api";
import type { Company } from "../../types/company";

interface Props {
  open: boolean;
  onClose: () => void;
  companyId: number;
  companyName: string;
}

/**
 * Modal that shows prep notes for a company, used from the Dashboard timeline.
 */
export default function PrepNotesModal({ open, onClose, companyId, companyName }: Props) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: company } = useQuery<Company>({
    queryKey: ["companies", companyId],
    queryFn: () => api.get<Company>(`/companies/${companyId}`),
    enabled: open && companyId > 0,
  });

  function handleClose() {
    queryClient.invalidateQueries({ queryKey: ["companies"] });
    onClose();
  }

  return (
    <Modal open={open} onClose={handleClose} title={`Prep Notes - ${companyName}`} width="max-w-2xl">
      {company ? (
        <div className="space-y-4">
          <PrepNotesTab
            companyId={companyId}
            initialNotes={company.prep_notes}
          />
          <div className="border-t border-gray-200 pt-3">
            <button
              type="button"
              onClick={() => {
                handleClose();
                navigate("/companies");
              }}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              View in Companies
            </button>
          </div>
        </div>
      ) : (
        <p className="text-sm text-gray-400 py-4">Loading...</p>
      )}
    </Modal>
  );
}
