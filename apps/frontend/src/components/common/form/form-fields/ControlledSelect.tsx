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
  options: baseOptions,
  showLabels,
}: BaseControlledPropsWithOptionsAndLabels) => {
  // Keep values that aren't in the option list (e.g. legacy free-text data) selectable
  const currentValue = field.value as string | undefined;
  const options =
    currentValue && !baseOptions.some((o) => o.value === currentValue)
      ? [{ label: currentValue, value: currentValue }, ...baseOptions]
      : baseOptions;

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
    <select className="max-w-fit" {...field} value={(field.value as string) ?? ""}>
      <option value="">—</option>
      {options.map((o, i) => (
        <option key={`${o.label}/${i}`} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
};

export default ControlledSelect;
