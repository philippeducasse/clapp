export const EMAIL_PLACEHOLDERS = [
  "{{firstName}}",
  "{{lastName}}",
  "{{companyName}}",
  "{{organisation}}",
  "{{currentYear}}",
] as const;

export const EMAIL_PLACEHOLDER_HELP_TEXT =
  `Use ${EMAIL_PLACEHOLDERS.join(", ")} as placeholders that will be replaced automatically.`;