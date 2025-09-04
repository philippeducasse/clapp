import React from "react";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { ControllerRenderProps } from "react-hook-form";

interface ControlledFileProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
}

const ControlledFile = ({ field }: ControlledFileProps) => {
  return (
    <div className="grid w-full max-w-sm items-center gap-3">
      <Input
        id={field.name}
        type="file"
        onChange={(e) => field.onChange(e.target.files?.[0])}
      />
    </div>
  );
};

export default ControlledFile;
