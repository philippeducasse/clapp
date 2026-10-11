import { describe, it, expect } from "vitest";
import { getNewContactEmails, mergeNewContacts } from "@/helpers/contactHelper";

describe("getNewContactEmails", () => {
  it("returns emails not already known", () => {
    expect(getNewContactEmails(["a@x.com", "b@x.com"], ["a@x.com"])).toEqual(["b@x.com"]);
  });

  it("compares case-insensitively and ignores whitespace", () => {
    expect(getNewContactEmails([" A@X.com "], ["a@x.com"])).toEqual([]);
  });

  it("skips invalid emails", () => {
    expect(getNewContactEmails(["not-an-email", "", "ok@x.com"], [])).toEqual(["ok@x.com"]);
  });

  it("deduplicates", () => {
    expect(getNewContactEmails(["a@x.com", "A@x.com"], [])).toEqual(["a@x.com"]);
  });

  it("ignores empty known emails", () => {
    expect(getNewContactEmails(["a@x.com"], ["", "b@x.com"])).toEqual(["a@x.com"]);
  });
});

describe("mergeNewContacts", () => {
  const existing = [{ id: 1, email: "a@x.com", name: "A" }];

  it("appends selected recipients as new contacts", () => {
    expect(mergeNewContacts(existing, ["b@x.com"], ["a@x.com", "b@x.com"])).toEqual([
      ...existing,
      { email: "b@x.com" },
    ]);
  });

  it("ignores selected emails that were removed from recipients", () => {
    expect(mergeNewContacts(existing, ["b@x.com"], ["a@x.com"])).toBeNull();
  });

  it("returns null when everything selected is already a contact", () => {
    expect(mergeNewContacts(existing, ["A@x.com"], ["A@x.com"])).toBeNull();
  });

  it("returns null when nothing is selected", () => {
    expect(mergeNewContacts(existing, [], ["b@x.com"])).toBeNull();
  });
});
