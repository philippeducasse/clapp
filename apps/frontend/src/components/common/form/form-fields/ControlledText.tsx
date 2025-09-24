import React from "react";
import { Input } from "@/components/ui/input";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { ControllerRenderProps } from "react-hook-form";

interface ControlledTextProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  type: ControlledFormElementType;
  showLabels: boolean;
}

const ControlledText = ({ field, type, showLabels }: ControlledTextProps) => {
  return showLabels ? (
    <Input type={type.toLowerCase()} {...field} value={field.value as string} />
  ) : (
    <input
      className="max-w-fit"
      type={type.toLowerCase()}
      {...field}
      value={field.value as string}
    />
  );
};

export default ControlledText;
