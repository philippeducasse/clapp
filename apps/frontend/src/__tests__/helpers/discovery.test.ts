import { describe, it, expect } from "vitest";
import { getSidebarItems, SIDEBAR_ITEMS } from "@/components/common/navigation/sidebarItems";
import {
  candidateApplicationDates,
  candidateDates,
  foundViaSummary,
  hopLabel,
  seedUrl,
} from "@/components/page-components/discover/helpers/discoveryLabels";
import {
  DiscoveryCandidate,
  DiscoveryCandidateState,
  DiscoveryOrgType,
} from "@/interfaces/entities/Discovery";

describe("sidebar items", () => {
  const titles = (isSuperuser: boolean | undefined) =>
    getSidebarItems(isSuperuser).map((item) => item.title);

  it("shows Discover to superusers only", () => {
    expect(titles(true)).toContain("Discover");
    expect(titles(false)).not.toContain("Discover");
    expect(titles(undefined)).not.toContain("Discover");
  });

  it("puts Discover right after Inbound emails", () => {
    const list = titles(true);
    expect(list.indexOf("Discover")).toBe(list.indexOf("Inbound emails") + 1);
  });

  it("keeps everything else for regular users", () => {
    expect(getSidebarItems(false)).toHaveLength(SIDEBAR_ITEMS.length - 1);
  });

  it("pushes Report a bug to the bottom whatever the filtering", () => {
    for (const isSuperuser of [true, false]) {
      const bottom = getSidebarItems(isSuperuser).filter((item) => item.bottom);
      expect(bottom.map((item) => item.title)).toEqual(["Report a bug"]);
    }
  });
});

const candidate = (fields: Partial<DiscoveryCandidate> = {}): DiscoveryCandidate => ({
  id: 1,
  run: 2,
  orgType: DiscoveryOrgType.FESTIVAL,
  state: DiscoveryCandidateState.PENDING,
  dismissReason: "",
  name: "Fest",
  description: "",
  country: "Belgium",
  town: "Namur",
  websiteUrl: "",
  domain: "",
  subtype: "",
  applicationType: "",
  applicationUrl: "",
  startDate: null,
  endDate: null,
  estimatedStartDate: null,
  approximateDate: "",
  applicationDateStart: "",
  applicationDateEnd: "",
  contacts: [],
  foundVia: [],
  sources: [],
  relevanceReason: "",
  createdSeed: null,
  createdAt: "2026-10-18T10:00:00Z",
  reviewedAt: null,
  ...fields,
});

describe("discovery labels", () => {
  it("describes the found-via path", () => {
    expect(
      foundViaSummary([
        { kind: "artist_site", url: "https://a.fr/" },
        { kind: "calendar", url: "https://a.fr/agenda/" },
        { kind: "festival_site", url: "https://f.be/" },
        { kind: "contact", url: "https://f.be/contact/" },
      ]),
    ).toBe("Artist site → Calendar → Festival site → Contact page");
    expect(hopLabel("ARTIST_SITE")).toBe("Artist site");
    expect(hopLabel("something_new")).toBe("Something new");
    expect(hopLabel(undefined)).toBe("Page");
  });

  it("links an accepted candidate to its seed", () => {
    expect(seedUrl(candidate())).toBeNull();
    expect(
      seedUrl(candidate({ createdSeed: { orgType: DiscoveryOrgType.RESIDENCY, id: 9 } })),
    ).toBe("/residencies/9");
  });

  it("formats dates", () => {
    expect(candidateDates(candidate({ startDate: "2027-06-11", endDate: "2027-06-13" }))).toBe(
      "11 Jun 2027 – 13 Jun 2027",
    );
    expect(candidateDates(candidate({ approximateDate: "mid June" }))).toBe("mid June");
    expect(candidateDates(candidate())).toBe("");
    expect(candidateApplicationDates(candidate({ applicationDateEnd: "2027-01-31" }))).toBe(
      "until 2027-01-31",
    );
  });
});
