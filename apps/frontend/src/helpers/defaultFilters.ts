import { EntityName, TableEntityName } from "@/interfaces/Enums";
import { Profile } from "@/interfaces/entities/Profile";
import { ColumnFilter } from "@/interfaces/table/FilterCongig";
import { getDefaultExcludedTagsFilter } from "@/helpers/tagFilters";

/**
 * A default filter rule: derives one column filter from the user's profile,
 * or returns undefined when it doesn't apply.
 */
export type DefaultFilterRule = (profile: Profile | null | undefined) => ColumnFilter | undefined;

// --- Rules -------------------------------------------------------------------

const defaultSeason: DefaultFilterRule = (profile) => {
  const season = profile?.applicationSeasons?.find((s) => s.isDefault);
  return season ? { id: "season", value: season.name } : undefined;
};

// Hide irrelevant/inactive organisations (see DEFAULT_EXCLUDED_TAGS).
const defaultExcludedTags: DefaultFilterRule = () => getDefaultExcludedTagsFilter();

// --- Registry ----------------------------------------------------------------
// To add a default filter, write a rule above and list it for its table.

const defaultFilterRules: Partial<Record<TableEntityName, DefaultFilterRule[]>> = {
  [EntityName.APPLICATION]: [defaultSeason],
  [EntityName.FESTIVAL]: [defaultExcludedTags],
  [EntityName.RESIDENCY]: [defaultExcludedTags],
  [EntityName.VENUE]: [defaultExcludedTags],
};

/** Default column filters for a table, derived from the user's profile. */
export const getDefaultFilters = (
  entityName: TableEntityName,
  profile: Profile | null | undefined,
): ColumnFilter[] =>
  (defaultFilterRules[entityName] ?? [])
    .map((rule) => rule(profile))
    .filter((filter): filter is ColumnFilter => filter !== undefined);

/** Converts column filters to the `{ [columnId]: value }` shape the API expects. */
export const toFilterParams = (filters: ColumnFilter[]): Record<string, unknown> =>
  Object.fromEntries(filters.map((filter) => [filter.id, filter.value]));
