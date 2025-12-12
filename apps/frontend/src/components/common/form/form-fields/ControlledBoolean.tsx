import React from "react";
import { Switch } from "@/components/ui/switch";
import { BaseControlledPropsWithLabels } from "@/interfaces/forms/ControlledFormFieldsProps";

const ControlledBoolean = ({ field, showLabels }: BaseControlledPropsWithLabels) => {
  return showLabels ? (
    <Switch className="my-4" checked={field?.value as boolean} onCheckedChange={field.onChange} />
  ) : (
    <input
      type="checkbox"
      className="p-2 mb-1 mt-0.5 mr-auto border-b align-baseline whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px] overflow-hidden truncate"
      checked={field.value as boolean}
      onChange={field.onChange}
    />
  );
};

export default ControlledBoolean;
