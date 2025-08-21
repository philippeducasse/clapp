import React from "react";
import { ControllerRenderProps } from "react-hook-form";
import { Switch } from "@/components/ui/switch";

interface ControlledBooleanProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
}

const ControlledBoolean = ({ field }: ControlledBooleanProps) => {
  return <Switch className="my-4" checked={field?.value as boolean} onCheckedChange={field.onChange} />;
};

export default ControlledBoolean;
