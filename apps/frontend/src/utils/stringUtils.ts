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

export function formatErrorMessage(message: string) {
  let errorMessage = message ?? "Error!";

  try {
    const errorJson = JSON.parse(errorMessage);
    errorMessage = errorJson.error;
  } catch {}

  return errorMessage;
}
