import { MultiSelect } from "@/components/ui/multi-select";
import { BaseControlledPropsWithOptions } from "@/interfaces/forms/ControlledFormFieldsProps";

const ControlledMultiSelect = ({ options, field }: BaseControlledPropsWithOptions) => {
  return (
    <MultiSelect
      options={options}
      value={(field.value as string[]) ?? []}
      onValueChange={(val) => {
        field.onChange(val);
      }}
    />
  );
};

export default ControlledMultiSelect;
