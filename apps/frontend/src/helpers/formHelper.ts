export const sanitizeFormData = <T extends Record<string, unknown>>(entity: T): { [K in keyof T]: string } => {
  const sanitizedData = {} as { [K in keyof T]: string };

  for (const key in entity) {
    if (Object.prototype.hasOwnProperty.call(entity, key)) {
      const value = entity[key];
      sanitizedData[key] = value !== null && value !== undefined ? String(value) : "";
    }
  }

  return sanitizedData;
};
