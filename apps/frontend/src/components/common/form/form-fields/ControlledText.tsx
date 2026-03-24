import React from "react";
import { Input } from "@/components/ui/input";
import { BaseControlledPropsWithType } from "@/interfaces/forms/ControlledFormFieldsProps";

const ControlledText = ({ field, type, showLabels }: BaseControlledPropsWithType) => {
  const t = type.toLowerCase();
  console.log({ t });
  return showLabels ? (
    <Input type={t === "url" ? "text" : t} {...field} value={field.value as string} />
  ) : (
    <input
      className="max-w-fit"
      type={t === "url" ? "text" : t}
      {...field}
      value={field.value as string}
    />
  );
};

export default ControlledText;
