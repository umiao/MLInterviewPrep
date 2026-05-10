import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { CompanyCard } from "./Companies";
import type { Company } from "../types/company";

function makeCompany(overrides: Partial<Company> = {}): Company {
  return {
    id: 1,
    name: "Acme",
    group_tag: null,
    interview_stages: [],
    status: "applied",
    applied_at: null,
    notes: null,
    prep_notes: null,
    has_meaningful_note: false,
    ...overrides,
  };
}

describe("<CompanyCard /> red-dot indicator", () => {
  it("renders red dot when has_meaningful_note=true and company is in pipeline", () => {
    const html = renderToStaticMarkup(
      <CompanyCard
        company={makeCompany({ has_meaningful_note: true })}
        onClick={() => {}}
      />,
    );
    expect(html).toContain("bg-red-500");
    expect(html).toContain("Has prep notes / docs / tagged content");
  });

  it("does not render red dot when has_meaningful_note=false", () => {
    const html = renderToStaticMarkup(
      <CompanyCard
        company={makeCompany({ has_meaningful_note: false })}
        onClick={() => {}}
      />,
    );
    expect(html).not.toContain("bg-red-500");
  });

  it("does not render red dot when company is rejected (out of pipeline)", () => {
    const html = renderToStaticMarkup(
      <CompanyCard
        company={makeCompany({
          has_meaningful_note: true,
          status: "rejected",
        })}
        onClick={() => {}}
      />,
    );
    expect(html).not.toContain("bg-red-500");
  });
});
