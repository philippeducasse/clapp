import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { BaseControlledPropsWithOptionsAndLabels } from "@/interfaces/forms/ControlledFormFieldsProps";

const ControlledSelect = ({
  field,
  options,
  showLabels,
}: BaseControlledPropsWithOptionsAndLabels) => {
  return showLabels ? (
    <Select
      defaultValue={field.value as string | undefined}
      value={field.value as string}
      onValueChange={(val) => {
        field.onChange(val);
      }}
    >
      <SelectTrigger>
        <SelectValue placeholder="Select an option" />
      </SelectTrigger>
      <SelectContent>
        {options.map((o, i) => (
          <SelectItem key={`${o.label}/${i}`} value={o.value}>
            {o.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  ) : (
    <select className="max-w-fit" {...field} value={field.value as string}>
      {options.map((o, i) => (
        <option key={`${o.label}/${i}`} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
};

export default ControlledSelect;
