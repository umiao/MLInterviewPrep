import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import Modal from "../ui/Modal";
import DrawerLayout from "../ui/DrawerLayout";
import { DRAWER_RESPONSIVE_WIDTH } from "../ui/SlideOverPanel";
import PrepNotesTab from "../companies/PrepNotesTab";
import { api } from "../../utils/api";
import type { Company, CompanyStatus } from "../../types/company";

interface Props {
  open: boolean;
  onClose: () => void;
  companyId: number;
  companyName: string;
}

const STATUS_STYLES: Record<CompanyStatus, string> = {
  applied: "bg-blue-100 text-blue-800 border-blue-200",
  phone_screen: "bg-indigo-100 text-indigo-800 border-indigo-200",
  onsite: "bg-amber-100 text-amber-800 border-amber-200",
  offer: "bg-emerald-100 text-emerald-800 border-emerald-200",
  rejected: "bg-gray-100 text-gray-700 border-gray-200",
};

function CompanyMetaPane({
  company,
  onViewInCompanies,
}: {
  company: Company;
  onViewInCompanies: () => void;
}) {
  return (
    <div className="space-y-4 text-sm">
      <div>
        <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">Company</div>
        <div className="font-bold text-gray-900 text-base">{company.name}</div>
        {company.group_tag && (
          <div className="text-xs text-gray-500 mt-0.5">{company.group_tag}</div>
        )}
      </div>

      <div>
        <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">Status</div>
        <span
          className={`inline-block text-xs font-semibold uppercase tracking-wider px-2 py-0.5 rounded border ${STATUS_STYLES[company.status]}`}
        >
          {company.status.replace("_", " ")}
        </span>
      </div>

      {company.applied_at && (
        <div>
          <div className="text-xs uppercase tracking-wider text-gray-500 mb-1">Applied</div>
          <div className="font-medium text-gray-800">{company.applied_at}</div>
        </div>
      )}

      <div className="pt-2 border-t border-gray-200">
        <button
          type="button"
          onClick={onViewInCompanies}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          View in Companies
        </button>
      </div>
    </div>
  );
}

/**
 * Modal that shows prep notes for a company, used from the Dashboard timeline.
 *
 * Uses the shared DrawerLayout for a responsive two-column layout: company
 * meta on the left (sticky at lg+) and the markdown prep notes editor on the
 * right with a 680px prose cap.
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

  function handleViewInCompanies() {
    handleClose();
    navigate("/companies");
  }

  return (
    <Modal
      open={open}
      onClose={handleClose}
      title={`Prep Notes - ${companyName}`}
      width={DRAWER_RESPONSIVE_WIDTH}
    >
      {company ? (
        <DrawerLayout
          left={
            <CompanyMetaPane
              company={company}
              onViewInCompanies={handleViewInCompanies}
            />
          }
          right={
            <PrepNotesTab
              companyId={companyId}
              initialNotes={company.prep_notes}
            />
          }
        />
      ) : (
        <p className="text-sm text-gray-400 py-4">Loading...</p>
      )}
    </Modal>
  );
}
