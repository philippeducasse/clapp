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
