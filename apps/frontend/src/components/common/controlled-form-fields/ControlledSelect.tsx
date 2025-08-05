import React from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ControllerRenderProps } from "react-hook-form";
import { SelectOptions } from "@/interfaces/ControlledFormElement";

interface ControlledSelectProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  options: SelectOptions[];
}

const ControlledSelect = ({ field, options }: Omit<ControlledSelectProps, "handleChange">) => {
  return (
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
  );
};

export default ControlledSelect;
