import React from "react";
import { ControllerRenderProps } from "react-hook-form";
import { Switch } from "@/components/ui/switch";

interface ControlledBooleanProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  // type: ControlledFormElementType;
  // handleChange: (field: keyof Festival) => (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const ControlledBoolean = ({ field }: ControlledBooleanProps) => {
  return <Switch checked={field?.value as boolean} onCheckedChange={field.onChange} />;
};

export default ControlledBoolean;
