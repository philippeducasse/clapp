import _ from "lodash";

/**
 * Capitalizes the first letter of a string after converting it to lowercase.
 * Useful for normalizing enum values or database strings for display.
 *
 * @param str - The string to capitalize
 * @returns The capitalized string
 *
 * @example
 * capitalizeFirst("HELLO_WORLD") // "Hello world"
 * capitalizeFirst("someValue") // "Somevalue"
 */
export const capitalizeFirst = (str: string | undefined | null): string => {
  if (!str) return "";
  return _.capitalize(_.lowerCase(str));
};

export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return (
    d.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }) +
    ", " +
    d.toLocaleTimeString("en-GB", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false,
    })
  );
}

export const transformKeysToCamelCase = (obj: any): any => {
  if (Array.isArray(obj)) {
    return obj.map((v) => transformKeysToCamelCase(v));
  } else if (obj != null && obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const camelKey = _.camelCase(key);
      result[camelKey] = transformKeysToCamelCase(obj[key]);
      return result;
    }, {} as any);
  }
  return obj;
};

export const transformKeysToSnakeCase = (obj: any): any => {
  if (Array.isArray(obj)) {
    return obj.map((v) => transformKeysToSnakeCase(v));
  } else if (obj && obj.constructor === Object) {
    return Object.keys(obj).reduce((result, key) => {
      const snakeKey = _.snakeCase(key);
      result[snakeKey] = transformKeysToSnakeCase(obj[key]);
      return result;
    }, {} as any);
  }
  return obj;
};

export function formatErrorMessage(message: string, maxLength = 100) {
  let errorMessage = message ?? "Error!";
  try {
    const errorJson = JSON.parse(errorMessage);
    if (typeof errorJson.error === "string") {
      errorMessage = errorJson.error;
    } else {
      const messages = Object.values(errorJson).flat();
      errorMessage = messages.join("; ");
    }
  } catch {}

  if (errorMessage?.length > maxLength) {
    return errorMessage.slice(0, maxLength) + "…";
  }
  return errorMessage;
}
