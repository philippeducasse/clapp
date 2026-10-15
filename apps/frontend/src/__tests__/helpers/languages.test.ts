import { describe, it, expect } from "vitest";
import {
  DEFAULT_LANGUAGE_CODE,
  LANGUAGES,
  getLanguageName,
  toLanguageOptions,
} from "@/constants/languages";

describe("languages", () => {
  it("uses unique two-letter lowercase ISO 639-1 codes", () => {
    const codes = LANGUAGES.map((l) => l.code);
    expect(new Set(codes).size).toBe(codes.length);
    codes.forEach((code) => expect(code).toMatch(/^[a-z]{2}$/));
  });

  it("includes the default language", () => {
    expect(LANGUAGES.some((l) => l.code === DEFAULT_LANGUAGE_CODE)).toBe(true);
  });

  it("maps codes to display names", () => {
    expect(getLanguageName("en")).toBe("English");
    expect(getLanguageName("de")).toBe("German");
  });

  it("falls back to the raw value for unknown codes", () => {
    expect(getLanguageName("xx")).toBe("xx");
    expect(getLanguageName("")).toBe("");
  });

  it("builds select options with code as value and name as label", () => {
    expect(toLanguageOptions([{ code: "fr", name: "French" }])).toEqual([
      { value: "fr", label: "French" },
    ]);
    expect(toLanguageOptions()).toHaveLength(LANGUAGES.length);
  });
});
