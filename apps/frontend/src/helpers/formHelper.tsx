import { ControlledFormElement } from "@/interfaces/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/ControlledFormElementType";
import { z, ZodObject, ZodType } from "zod";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { UseFormReturn } from "react-hook-form";
import { ControllerRenderProps } from "react-hook-form";
import ControlledSelect from "@/components/common/ControlledFormFields/ControlledSelect";
import DefaultInput from "@/components/common/ControlledFormFields/DefaultInput";
import { Festival } from "@/interfaces/Festival";

export const createFormComponents = (
  formFields: ControlledFormElement[],
  form: UseFormReturn<Record<string, unknown>, any, Record<string, unknown>>,
  formSchema: z.ZodObject<any, z.core.$strip>,
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void
) => {
  return formFields.map((formField) => (
    <FormField
      key={formField.fieldName}
      control={form.control}
      name={formField.fieldName as keyof z.infer<typeof formSchema>}
      render={({ field }) => (
        <FormItem>
          <FormLabel>{formField.label}</FormLabel>
          <FormControl>
            {formField.type === ControlledFormElementType.SELECT ? (
              <ControlledSelect {...field} />
            ) : (
              <DefaultInput field={field} type={formField.type} handleChange={handleChange} />
            )}
          </FormControl>
          {formField.helpText && <FormDescription>{formField.helpText}</FormDescription>}
          <FormMessage />
        </FormItem>
      )}
    />
  ));
};

export const sanitizeFormData = <T extends Record<string, any>>(entity: T): T => {
  const sanitizedData = { ...entity } as T; // Assert the type of sanitizedData as T

  for (const key in sanitizedData) {
    if (Object.prototype.hasOwnProperty.call(sanitizedData, key)) {
      const value = sanitizedData[key];
      // Replace null or undefined with undefined
      if (value === null || value === undefined) {
        sanitizedData[key] = undefined!; // Use non-null assertion to inform TypeScript
      }
    }
  }

  return sanitizedData;
};

export const createZodFormSchema = (formFields: ControlledFormElement[]): ZodObject<any> => {
  const schema: Record<string, ZodType> = {};

  formFields.forEach((field) => {
    const { fieldName, type, required } = field;
    let zodType: ZodType;

    switch (type) {
      case ControlledFormElementType.NUMBER:
        zodType = z.number();
        break;

      case ControlledFormElementType.SELECT:
        zodType = z.string();
        break;

      case ControlledFormElementType.BOOLEAN:
        zodType = z.boolean();

      case ControlledFormElementType.FILE:
        zodType = z.instanceof(File);
        break;

      case ControlledFormElementType.DATE:
        zodType = z.date();
        break;

      case ControlledFormElementType.TEXT:
        zodType = z.string();
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
      schema[fieldName] = zodType.optional();
    }
  });
  return z.object(schema);
};
