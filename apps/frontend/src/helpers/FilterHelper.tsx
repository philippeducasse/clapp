import { FilterType } from "@/interfaces/forms/ControlledFormElementType";
import { FilterConfig } from "@/interfaces/table/FilterCongig";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Column } from "@tanstack/table-core";

export const getFilterInput = (
  filterConfig: FilterConfig,
  value: string,
  column: Column<TData>
) => {
  console.log("FILTER:", filterConfig, "VAL:", value);
  switch (filterConfig.type) {
    case FilterType.SELECT:
      return filterConfig.options ? (
        <Select value={value} onValueChange={(event) => column?.setFilterValue(event || undefined)}>
          <SelectTrigger>
            <SelectValue placeholder={`Select ${filterConfig.label}`} />
          </SelectTrigger>
          <SelectContent>
            {filterConfig.options.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      ) : null;

    case FilterType.MULTI_SELECT:
      return filterConfig.options ? (
        <Select value={value} onValueChange={(event) => column?.setFilterValue(event || undefined)}>
          <SelectTrigger>
            <SelectValue placeholder={`Select ${filterConfig.label}`} />
          </SelectTrigger>
          <SelectContent>
            {filterConfig.options.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      ) : null;

    case FilterType.NUMBER:
      return (
        <Input
          type="number"
          value={value || ""}
          onChange={(event) => column?.setFilterValue(event || undefined)}
          placeholder={filterConfig.label}
        />
      );

    case FilterType.DATE:
      return (
        <Input
          type="date"
          value={value || ""}
          onChange={(event) => column?.setFilterValue(event || undefined)}
          placeholder={filterConfig.label}
        />
      );

    case FilterType.TEXT:
    default:
      return (
        <Input
          type="text"
          value={value || ""}
          onChange={(event) => column?.setFilterValue(event || undefined)}
          placeholder={filterConfig.label}
        />
      );
  }
};
