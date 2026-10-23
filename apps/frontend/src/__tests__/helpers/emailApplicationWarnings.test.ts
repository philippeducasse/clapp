import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  buildEmailApplicationWarnings,
  getDateMonthsAgo,
  hasRecentApplication,
} from "@/components/page-components/applications/helpers/getEmailApplicationWarnings";
import { applicationApiService } from "@/api/applicationApiService";

vi.mock("@/api/applicationApiService", () => ({
  applicationApiService: { getAll: vi.fn() },
}));

describe("getDateMonthsAgo", () => {
  it("returns the date six months earlier as YYYY-MM-DD", () => {
    expect(getDateMonthsAgo(6, new Date(2026, 9, 23))).toBe("2026-04-23");
  });

  it("crosses year boundaries", () => {
    expect(getDateMonthsAgo(6, new Date(2026, 1, 5))).toBe("2025-08-05");
  });
});

describe("buildEmailApplicationWarnings", () => {
  it("returns no warnings for an email organisation with no recent application", () => {
    expect(
      buildEmailApplicationWarnings({
        organisationName: "Fest",
        applicationType: "EMAIL",
        hasRecentApplication: false,
      }),
    ).toEqual([]);
  });

  it("warns when the organisation takes applications by form", () => {
    const warnings = buildEmailApplicationWarnings({
      organisationName: "Fest",
      applicationType: "FORM",
      hasRecentApplication: false,
    });
    expect(warnings).toHaveLength(1);
    expect(warnings[0]).toContain("form");
  });

  it("warns when there is a recent application", () => {
    const warnings = buildEmailApplicationWarnings({
      organisationName: "Fest",
      applicationType: undefined,
      hasRecentApplication: true,
    });
    expect(warnings).toHaveLength(1);
    expect(warnings[0]).toContain("last 6 months");
  });

  it("returns both warnings when both apply", () => {
    expect(
      buildEmailApplicationWarnings({
        organisationName: "Fest",
        applicationType: "FORM",
        hasRecentApplication: true,
      }),
    ).toHaveLength(2);
  });

  it("falls back to a generic name", () => {
    const [warning] = buildEmailApplicationWarnings({ hasRecentApplication: true });
    expect(warning).toContain("this organisation");
  });
});

describe("hasRecentApplication", () => {
  beforeEach(() => vi.mocked(applicationApiService.getAll).mockReset());

  it("queries applications for the organisation in the last 6 months", async () => {
    vi.mocked(applicationApiService.getAll).mockResolvedValue({ count: 1 } as never);

    await expect(hasRecentApplication("Festival", 12)).resolves.toBe(true);
    expect(applicationApiService.getAll).toHaveBeenCalledWith({
      limit: 1,
      filters: {
        organisationType: "Festival",
        organisation: 12,
        appliedAfter: getDateMonthsAgo(6),
      },
    });
  });

  it("returns false when there are none", async () => {
    vi.mocked(applicationApiService.getAll).mockResolvedValue({ count: 0 } as never);
    await expect(hasRecentApplication("Venue", 3)).resolves.toBe(false);
  });
});
