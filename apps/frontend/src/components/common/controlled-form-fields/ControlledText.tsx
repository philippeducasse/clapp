import React from "react";
import { Input } from "@/components/ui/input";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";
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
      // className="p-2 border-b align-middle whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px] overflow-hidden truncate"
      type={type.toLowerCase()}
      {...field}
      value={field.value as string}
    />
  );
};

export default ControlledText;
