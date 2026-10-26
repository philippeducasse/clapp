import { describe, it, expect } from "vitest";
import {
  DEFAULT_EXCLUDED_TAGS,
  EXCLUDE_TAG_FILTER_ID,
  getDefaultExcludedTagsFilter,
  getTagFilterConfigs,
  matchesExcludedTags,
  matchesIncludedTags,
} from "@/helpers/tagFilters";
import { buildQueryParams } from "@/api/helpers/buildQueryParams";
import { toFilterParams } from "@/helpers/defaultFilters";
import { TagAction } from "@/interfaces/Enums";

describe("matchesIncludedTags", () => {
  it("passes everything when nothing is selected", () => {
    expect(matchesIncludedTags("STAR", undefined)).toBe(true);
    expect(matchesIncludedTags(undefined, [])).toBe(true);
  });

  it("passes only rows with a selected tag", () => {
    expect(matchesIncludedTags("STAR", ["STAR", "WATCH"])).toBe(true);
    expect(matchesIncludedTags("INACTIVE", ["STAR", "WATCH"])).toBe(false);
    expect(matchesIncludedTags(undefined, ["STAR"])).toBe(false);
    expect(matchesIncludedTags("", ["STAR"])).toBe(false);
  });

  it("ignores non-array filter values", () => {
    expect(matchesIncludedTags("STAR", "WATCH")).toBe(true);
  });
});

describe("matchesExcludedTags", () => {
  const hidden = ["IRRELEVANT", "INACTIVE"];

  it("drops rows with an excluded tag", () => {
    expect(matchesExcludedTags("IRRELEVANT", hidden)).toBe(false);
    expect(matchesExcludedTags("INACTIVE", hidden)).toBe(false);
  });

  it("keeps rows with other tags", () => {
    expect(matchesExcludedTags("STAR", hidden)).toBe(true);
  });

  it("always keeps untagged rows", () => {
    expect(matchesExcludedTags(undefined, hidden)).toBe(true);
    expect(matchesExcludedTags("", hidden)).toBe(true);
  });

  it("keeps everything when nothing is excluded or the value is invalid", () => {
    expect(matchesExcludedTags("IRRELEVANT", undefined)).toBe(true);
    expect(matchesExcludedTags("IRRELEVANT", [])).toBe(true);
    expect(matchesExcludedTags("IRRELEVANT", "IRRELEVANT")).toBe(true);
  });
});

describe("getTagFilterConfigs", () => {
  it("offers every tag for both include and exclude", () => {
    const [include, exclude] = getTagFilterConfigs();
    const values = Object.values(TagAction);

    expect(include.column).toBe("tag");
    expect(include.options?.map((o) => o.value)).toEqual(values);
    expect(exclude.column).toBe(EXCLUDE_TAG_FILTER_ID);
    expect(exclude.options?.map((o) => o.value)).toEqual(values);
    expect(exclude.chipPrefix).toBe("Not");
  });

  it("labels tags in sentence case", () => {
    const [include] = getTagFilterConfigs();
    expect(include.options?.find((o) => o.value === TagAction.IRRELEVANT)?.label).toBe(
      "Irrelevant",
    );
  });
});

describe("default excluded tags", () => {
  it("hides irrelevant and inactive", () => {
    expect(DEFAULT_EXCLUDED_TAGS).toEqual([TagAction.IRRELEVANT, TagAction.INACTIVE]);
    expect(getDefaultExcludedTagsFilter()).toEqual({
      id: "excludeTag",
      value: ["IRRELEVANT", "INACTIVE"],
    });
  });

  it("is sent to the API as exclude_tag", () => {
    const query = buildQueryParams({
      filters: toFilterParams([getDefaultExcludedTagsFilter()]),
    });
    expect(new URLSearchParams(query).get("exclude_tag")).toBe("IRRELEVANT,INACTIVE");
  });
});
