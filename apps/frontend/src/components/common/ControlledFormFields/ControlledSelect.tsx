import React from "react";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ControllerRenderProps } from "react-hook-form";
import { Festival } from "@/interfaces/Festival";
import { SelectOptions } from "@/interfaces/ControlledFormElement";

interface DefaultInputProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  options: SelectOptions[];
  handleChange: (field: keyof Festival) => (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const ControlledSelect = ({ field, options, handleChange }: DefaultInputProps) => {
  return (
    <Select
      value={field.value as string | undefined}
      onValueChange={(val) => {
        field.onChange(val);
        handleChange;
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
