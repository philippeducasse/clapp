import React from "react";
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
        multiple
        onChange={(e) =>
          field.onChange(e.target.files ? Array.from(e.target.files) : [])
        }
      />
    </div>
  );
};

export default ControlledFile;
