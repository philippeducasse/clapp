import { describe, it, expect } from "vitest";
import {
  getDetailsLostOnConversion,
  ORGANISATION_ROUTES,
  ORGANISATION_TYPE_LABELS,
} from "@/helpers/organisationRoutes";
import { OrganisationType } from "@/interfaces/Enums";

const { FESTIVAL, VENUE, RESIDENCY } = OrganisationType;

describe("organisation maps", () => {
  it("has a route and label for every type", () => {
    for (const type of Object.values(OrganisationType)) {
      expect(ORGANISATION_ROUTES[type]).toMatch(/^\/[a-z]+$/);
      expect(ORGANISATION_TYPE_LABELS[type]).toBeTruthy();
    }
  });
});

describe("getDetailsLostOnConversion", () => {
  it.each([
    [FESTIVAL, VENUE, ["festival type", "dates", "application details"]],
    [FESTIVAL, RESIDENCY, ["festival type"]],
    [RESIDENCY, FESTIVAL, []],
    [RESIDENCY, VENUE, ["dates", "application details"]],
    [VENUE, FESTIVAL, ["venue type", "contacted status"]],
    [VENUE, RESIDENCY, ["venue type", "contacted status"]],
  ])("%s -> %s loses %j", (from, to, lost) => {
    expect(getDetailsLostOnConversion(from, to)).toEqual(lost);
  });

  it("loses nothing when the type doesn't change", () => {
    expect(getDetailsLostOnConversion(FESTIVAL, FESTIVAL)).toEqual([]);
  });
});
