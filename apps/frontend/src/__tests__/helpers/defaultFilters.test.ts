import { describe, it, expect } from "vitest";
import { getDefaultFilters, toFilterParams } from "@/helpers/defaultFilters";
import { EntityName } from "@/interfaces/Enums";
import { Profile } from "@/interfaces/entities/Profile";

const profile = (overrides: Partial<Profile> = {}): Profile => ({
  id: 1,
  email: "test@example.com",
  firstName: "John",
  lastName: "Doe",
  confirmedAccount: true,
  performances: [],
  ...overrides,
});

describe("getDefaultFilters", () => {
  describe("applications", () => {
    it("filters on the default season", () => {
      expect(
        getDefaultFilters(
          EntityName.APPLICATION,
          profile({
            applicationSeasons: [
              { id: 1, name: "2025", isDefault: false },
              { id: 2, name: "2026", isDefault: true },
            ],
          }),
        ),
      ).toEqual([{ id: "season", value: "2026" }]);
    });

    it("returns no filters when no season is the default", () => {
      expect(
        getDefaultFilters(
          EntityName.APPLICATION,
          profile({ applicationSeasons: [{ id: 1, name: "2025" }] }),
        ),
      ).toEqual([]);
    });

    it("returns no filters when the profile has no seasons", () => {
      expect(getDefaultFilters(EntityName.APPLICATION, profile())).toEqual([]);
    });

    it("returns no filters without a profile", () => {
      expect(getDefaultFilters(EntityName.APPLICATION, null)).toEqual([]);
      expect(getDefaultFilters(EntityName.APPLICATION, undefined)).toEqual([]);
    });
  });

  describe("organisations", () => {
    const organisationTables = [EntityName.FESTIVAL, EntityName.VENUE, EntityName.RESIDENCY] as const;

    it.each(organisationTables)("%s hides irrelevant and inactive tags", (entity) => {
      expect(getDefaultFilters(entity, null)).toEqual([
        { id: "excludeTag", value: ["IRRELEVANT", "INACTIVE"] },
      ]);
    });

    it.each(organisationTables)("%s does not use the application season", (entity) => {
      const p = profile({ applicationSeasons: [{ id: 2, name: "2026", isDefault: true }] });
      expect(getDefaultFilters(entity, p).map((f) => f.id)).toEqual(["excludeTag"]);
    });

    it("returns a fresh array each call so callers can't mutate the defaults", () => {
      const first = getDefaultFilters(EntityName.FESTIVAL, null)[0].value as string[];
      first.push("STAR");
      expect(getDefaultFilters(EntityName.FESTIVAL, null)[0].value).toEqual([
        "IRRELEVANT",
        "INACTIVE",
      ]);
    });
  });
});

describe("toFilterParams", () => {
  it("maps column filters to API params", () => {
    expect(
      toFilterParams([
        { id: "season", value: "2026" },
        { id: "status", value: "APPLIED" },
      ]),
    ).toEqual({ season: "2026", status: "APPLIED" });
  });

  it("keeps array values (joined to exclude_tag=IRRELEVANT,INACTIVE by buildQueryParams)", () => {
    expect(toFilterParams([{ id: "excludeTag", value: ["IRRELEVANT", "INACTIVE"] }])).toEqual({
      excludeTag: ["IRRELEVANT", "INACTIVE"],
    });
  });

  it("returns an empty object for no filters", () => {
    expect(toFilterParams([])).toEqual({});
  });
});
