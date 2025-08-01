import React from "react";
import { Input } from "@/components/ui/input";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";
import { ControllerRenderProps } from "react-hook-form";

interface ControlledTextProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  type: ControlledFormElementType;
}

const ControlledText = ({ field, type }: ControlledTextProps) => {
  return <Input type={type.toLowerCase()} {...field} value={field.value as string} />;
};

export default ControlledText;
