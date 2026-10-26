import { ColumnDef, FilterFn } from "@tanstack/react-table";
import { capitalizeFirst } from "@/utils/stringUtils";
import { TagAction } from "@/interfaces/Enums";
import { ColumnFilter, FilterConfig } from "@/interfaces/table/FilterCongig";
import { FilterType } from "@/interfaces/forms/ControlledFormElementType";

/**
 * Tag filtering for organisation tables (festivals, residencies, venues).
 *
 * - `tag`        → keep only rows with one of the selected tags (`?tag=` on the API)
 * - `excludeTag` → drop rows with one of the selected tags (`?exclude_tag=` on the API).
 *                  Untagged rows are always kept. Applied by default (see DEFAULT_EXCLUDED_TAGS).
 */

export const TAG_FILTER_ID = "tag";
export const EXCLUDE_TAG_FILTER_ID = "excludeTag";

/** Tags hidden from organisation tables unless the user removes the filter. */
export const DEFAULT_EXCLUDED_TAGS: TagAction[] = [TagAction.IRRELEVANT, TagAction.INACTIVE];

// Built here rather than with formHelper's getOptions, which pulls in form components;
// this module is also used by Redux slices and server pages via defaultFilters.
const tagOptions = Object.values(TagAction).map((tag) => ({ value: tag, label: capitalizeFirst(tag) }));

const selectedTags = (filterValue: unknown): string[] =>
  Array.isArray(filterValue) ? filterValue : [];

/** True if `tag` passes the include filter (no selection = everything passes). */
export const matchesIncludedTags = (tag: string | undefined, filterValue: unknown): boolean => {
  const tags = selectedTags(filterValue);
  return tags.length === 0 || tags.includes(tag ?? "");
};

/** True if `tag` passes the exclude filter (untagged rows always pass). */
export const matchesExcludedTags = (tag: string | undefined, filterValue: unknown): boolean =>
  !tag || !selectedTags(filterValue).includes(tag);

export const includeTagFilterFn = <T>(): FilterFn<T> => (row, columnId, filterValue) =>
  matchesIncludedTags(row.getValue<string | undefined>(columnId), filterValue);

/**
 * Filter-only column holding the `excludeTag` filter. Hidden from the table
 * (see `meta.hidden` in DataTable); add it to an organisation table's columns.
 */
export const getExcludeTagColumn = <T extends { tag?: string }>(): ColumnDef<T> => ({
  id: EXCLUDE_TAG_FILTER_ID,
  accessorFn: (row) => row.tag ?? "",
  enableSorting: false,
  enableGlobalFilter: false,
  meta: { hidden: true },
  filterFn: (row, columnId, filterValue) =>
    matchesExcludedTags(row.getValue<string>(columnId), filterValue),
});

/** "Tags" and "Hide tags" filter configs for an organisation table's filter dialog. */
export const getTagFilterConfigs = (): FilterConfig[] => [
  {
    column: TAG_FILTER_ID,
    label: "Tags",
    type: FilterType.MULTI_SELECT,
    options: tagOptions,
    multiple: true,
  },
  {
    column: EXCLUDE_TAG_FILTER_ID,
    label: "Hide tags",
    type: FilterType.MULTI_SELECT,
    options: tagOptions,
    multiple: true,
    chipPrefix: "Not",
  },
];

/** Default column filter hiding DEFAULT_EXCLUDED_TAGS. */
export const getDefaultExcludedTagsFilter = (): ColumnFilter => ({
  id: EXCLUDE_TAG_FILTER_ID,
  value: [...DEFAULT_EXCLUDED_TAGS],
});
