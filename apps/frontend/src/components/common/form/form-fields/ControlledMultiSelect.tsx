import { MultiSelect } from "@/components/ui/multi-select";
import { SelectOptions } from "@/interfaces/forms/ControlledFormElement";
import { ControllerRenderProps } from "react-hook-form";

interface MultiSelectProps {
  field: ControllerRenderProps<Record<string, unknown>, string>;
  options: SelectOptions[];
}

const ControlledMultiSelect = ({ options, field }: MultiSelectProps) => {
  return (
    <MultiSelect
      options={options}
      onValueChange={(val) => {
        field.onChange(val);
      }}
      //   placeholder=""
    />
  );
};

export default ControlledMultiSelect;
