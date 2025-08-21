import React from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ControllerRenderProps } from "react-hook-form";
import { SelectOptions } from "@/interfaces/ControlledFormElement";

interface ControlledSelectProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  options: SelectOptions[];
  showLabels: boolean;
}

const ControlledSelect = ({ field, options, showLabels }: ControlledSelectProps) => {
  return showLabels ? (
    <Select
      value={field.value as string | undefined}
      onValueChange={(val) => {
        field.onChange(val);
      }}
    >
      <SelectTrigger>
        <SelectValue placeholder="Select a type" />
      </SelectTrigger>
      <SelectContent>
        {options.map((o, i) => (
          <SelectItem key={`${o.label}/${i}`} value={o.value}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  ) : (
    <select className="py-0.5 " {...field} value={field.value as string}>
      {options.map((o, i) => (
        <option key={`${o.label}/${i}`} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
};

export default ControlledSelect;
