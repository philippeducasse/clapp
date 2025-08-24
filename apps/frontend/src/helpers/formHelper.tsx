import { ControlledFormElement, SelectOptions } from "@/interfaces/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";
import { z, ZodObject, ZodType } from "zod";
import { capitalize } from "lodash";
import ControlledBoolean from "@/components/common/form/form-fields/ControlledBoolean";
import ControlledSelect from "@/components/common/form/form-fields/ControlledSelect";
import ControlledText from "@/components/common/form/form-fields/ControlledText";
import ControlledTextArea from "@/components/common/form/form-fields/ControlledTextArea";
import { ControllerRenderProps } from "react-hook-form";

export const getFestivalControlledInputs = (
  formField: ControlledFormElement,
  field: ControllerRenderProps,
  showLabels: boolean
) => {
  if (formField.hidden) return;
  {
    switch (formField.type) {
      case ControlledFormElementType.SELECT:
        return formField.options ? (
          <ControlledSelect field={field} options={formField.options} showLabels={showLabels} />
        ) : null;
      case ControlledFormElementType.BOOLEAN:
        return <ControlledBoolean field={field} showLabels={showLabels} />;
      case ControlledFormElementType.TEXT_AREA:
        return <ControlledTextArea field={field} showLabels={showLabels} />;
      default:
        return <ControlledText field={field} type={formField.type} showLabels={showLabels} />;
    }
  }
};

export const sanitizeFormData = <T extends Record<string, unknown>>(entity: T): T => {
  const sanitizedData = { ...entity } as T;

  for (const key in sanitizedData) {
    if (Object.prototype.hasOwnProperty.call(sanitizedData, key)) {
      const value = sanitizedData[key];
      // Replace null or undefined with an empty string to prevent uncontrolled inputs
      if (value === null || value === undefined) {
        sanitizedData[key] = "" as T[Extract<keyof T, string>];
      }
    }
  }

  return sanitizedData;
};

export const createZodFormSchema = (formFields: ControlledFormElement[]): ZodObject<Record<string, ZodType>> => {
  const schema: Record<string, ZodType> = {};

  formFields.forEach((field) => {
    const { fieldName, type, required } = field;
    let zodType: ZodType;

    switch (type) {
      case ControlledFormElementType.NUMBER:
        zodType = z.number();
        break;

      case ControlledFormElementType.SELECT:
      case ControlledFormElementType.TEXT:
      case ControlledFormElementType.TEXT_AREA:
        zodType = z.string();
        break;

      case ControlledFormElementType.BOOLEAN:
        zodType = z.boolean();
        break;

      case ControlledFormElementType.FILE:
        zodType = z.instanceof(File);
        break;

      case ControlledFormElementType.DATE:
        zodType = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Date must be in the format YYYY-MM-DD");
        break;

      case ControlledFormElementType.URL:
        zodType = z.url();
        break;
      case ControlledFormElementType.EMAIL:
        zodType = z.email();
        break;
    }

    if (required) {
      schema[fieldName] = zodType;
    } else {
      schema[fieldName] = zodType.optional().or(z.literal(""));
    }
  });
  return z.object(schema);
};

export const getOptions = <T extends Record<string, string>>(optionsEnum: T): SelectOptions[] => {
  const options = Object.values(optionsEnum).map((o) => ({
    value: o.toUpperCase(),
    label: capitalize(o.replace(/_/g, " ").toLowerCase()),
  }));
  return options;
};
