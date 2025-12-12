import React from "react";
import { Input } from "@/components/ui/input";
import { BaseControlledPropsWithType } from "@/interfaces/forms/ControlledFormFieldsProps";

const ControlledText = ({ field, type, showLabels }: BaseControlledPropsWithType) => {
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
