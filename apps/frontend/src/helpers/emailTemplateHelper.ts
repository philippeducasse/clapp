interface EmailTemplateVariables {
  firstName?: string;
  lastName?: string;
  entityName?: string;
  currentYear?: number;
}

/**
 * Interpolates template variables in an email subject template.
 * Supports: {{firstName}}, {{lastName}}, {{entityName}}, {{currentYear}}
 */
export const interpolateEmailTemplate = (
  template: string | undefined,
  variables: EmailTemplateVariables
): string => {
  if (!template) return "";

  let result = template;

  if (variables.firstName) {
    result = result.replace(/{{firstName}}/g, variables.firstName);
  }
  if (variables.lastName) {
    result = result.replace(/{{lastName}}/g, variables.lastName);
  }
  if (variables.entityName) {
    result = result.replace(/{{entityName}}/g, variables.entityName);
  }
  if (variables.currentYear) {
    result = result.replace(/{{currentYear}}/g, String(variables.currentYear));
  }

  // Remove any remaining unreplaced placeholders
  result = result.replace(/{{[^}]+}}/g, "");

  return result;
};
