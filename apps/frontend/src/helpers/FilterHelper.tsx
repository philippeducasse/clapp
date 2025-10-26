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
import { Label } from "@/components/ui/label";
import { Column } from "@tanstack/table-core";
import { Switch } from "@/components/ui/switch";

export const getFilterInput = <TData,>(
  filterConfig: FilterConfig,
  value: string,
  column: Column<TData>
) => {
  const renderInput = () => {
    switch (filterConfig.type) {
      case FilterType.SELECT:
        return filterConfig.options ? (
          <Select
            value={value}
            onValueChange={(event) => column?.setFilterValue(event || undefined)}
          >
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
          <Select
            value={value}
            onValueChange={(event) => column?.setFilterValue(event || undefined)}
          >
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
            placeholder={`Enter ${filterConfig.label.toLowerCase()}`}
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
      case FilterType.BOOLEAN:
        return (
          <Switch
            value={value || ""}
            onChange={(event) => column?.setFilterValue(event || undefined)}
          />
        );

      case FilterType.TEXT:
      default:
        return (
          <Input
            type="text"
            value={value || ""}
            onChange={(event) => column?.setFilterValue(event || undefined)}
            placeholder={`Search ${filterConfig.label.toLowerCase()}`}
          />
        );
    }
  };

  const input = renderInput();
  if (!input) return null;

  return (
    <div className=" flex w-full justify-evenly items-center">
      <Label className="text-sm font-medium">{filterConfig.label}</Label>
      {input}
    </div>
  );
};
