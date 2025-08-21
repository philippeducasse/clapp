import React from "react";
import { ControllerRenderProps } from "react-hook-form";
import { Switch } from "@/components/ui/switch";

interface ControlledBooleanProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  showLabels: boolean;
}

const ControlledBoolean = ({ field, showLabels }: ControlledBooleanProps) => {
  return showLabels ? (
    <Switch className="my-4" checked={field?.value as boolean} onCheckedChange={field.onChange} />
  ) : (
    <input
      type="checkbox"
      className="p-2 my-0.5 mr-auto border-b align-baseline whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px] overflow-hidden truncate"
      checked={field.value as boolean}
      onChange={field.onChange}
    />
  );
};

export default ControlledBoolean;
