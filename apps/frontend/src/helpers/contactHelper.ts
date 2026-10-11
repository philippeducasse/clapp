import { z } from "zod";
import { OrganisationContact } from "@/interfaces/entities/OrganisationContact";

const normalize = (email: string) => email.trim().toLowerCase();

/**
 * Returns the valid emails from `emails` that are not already in `knownEmails`
 * (case-insensitive), without duplicates.
 */
export const getNewContactEmails = (emails: string[], knownEmails: string[]): string[] => {
  const seen = new Set(knownEmails.filter(Boolean).map(normalize));
  const result: string[] = [];
  for (const email of emails) {
    const key = normalize(email);
    if (!key || seen.has(key) || !z.email().safeParse(email.trim()).success) continue;
    seen.add(key);
    result.push(email.trim());
  }
  return result;
};

/**
 * Appends contacts for `emailsToAdd` that are present in `recipients`
 * and not already in `contacts`. Returns null if nothing needs adding.
 */
export const mergeNewContacts = (
  contacts: OrganisationContact[],
  emailsToAdd: string[],
  recipients: string[],
): OrganisationContact[] | null => {
  const recipientKeys = new Set(recipients.map(normalize));
  const newEmails = getNewContactEmails(
    emailsToAdd.filter((email) => recipientKeys.has(normalize(email))),
    contacts.map((c) => c.email),
  );
  if (!newEmails.length) return null;
  return [...contacts, ...newEmails.map((email) => ({ email }))];
};
