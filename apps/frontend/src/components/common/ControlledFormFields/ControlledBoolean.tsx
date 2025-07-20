import React from "react";
import { Input } from "@/components/ui/input";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";
import { ControllerRenderProps } from "react-hook-form";
import { Festival } from "@/interfaces/Festival";
import { Switch } from "@/components/ui/switch";

interface ControlledBooleanProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  // type: ControlledFormElementType;
  // handleChange: (field: keyof Festival) => (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const ControlledBoolean = ({ field }: ControlledBooleanProps) => {
  console.log("field:", field);
  return <Switch checked={field?.value as boolean} onCheckedChange={field.onChange} />;
};

export default ControlledBoolean;
