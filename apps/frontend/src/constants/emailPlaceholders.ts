export const EMAIL_PLACEHOLDERS = [
  "{{firstName}}",
  "{{lastName}}",
  "{{companyName}}",
  "{{organisation}}",
  "{{currentYear}}",
] as const;

export const EMAIL_PLACEHOLDER_HELP_TEXT = `Use ${EMAIL_PLACEHOLDERS.join(", ")} as placeholders that will be replaced automatically. For example, if you want your default email subject to be MyCompanyName at OrganisationImAPplyingTo 2027, you would write {{companyName}} at {{organisation}} 2027`;
