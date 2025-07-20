import React from "react";
import { Input } from "@/components/ui/input";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";
import { ControllerRenderProps } from "react-hook-form";
import { Festival } from "@/interfaces/Festival";

interface ControlledTextProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  type: ControlledFormElementType;
  handleChange: (field: keyof Festival) => (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const ControlledText = ({ field, type, handleChange }: ControlledTextProps) => {
  return (
    <Input
      type={type.toLowerCase()}
      {...field}
      value={field.value as string}
      onChange={(e) => {
        field.onChange(e);
        handleChange(field as unknown as keyof Festival)(e);
      }}
    />
  );
};

export default ControlledText;
