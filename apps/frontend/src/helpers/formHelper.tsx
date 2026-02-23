import { ControlledFormElement, SelectOptions } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { z, ZodObject, ZodType } from "zod";
import { capitalize } from "lodash";
import ControlledBoolean from "@/components/common/form/form-fields/ControlledBoolean";
import ControlledSelect from "@/components/common/form/form-fields/ControlledSelect";
import ControlledText from "@/components/common/form/form-fields/ControlledText";
import ControlledTextArea from "@/components/common/form/form-fields/ControlledTextArea";
import { ControllerRenderProps } from "react-hook-form";
import { ControlledTextEditor } from "@/components/common/form/form-fields/ControlledTextEditor";
import ControlledFile from "@/components/common/form/form-fields/ControlledFile";
import ControlledSingleFile from "@/components/common/form/form-fields/ControlledSingleFile";
import ControlledMultiSelect from "@/components/common/form/form-fields/ControlledMultiSelect";
import ControlledSearch from "@/components/common/form/form-fields/ControlledSearch";
import ControlledMultiEmail from "@/components/common/form/form-fields/ControlledMultiEmail";
import { Input } from "@/components/ui/input";
import ControlledSlider from "@/components/common/form/form-fields/ControlledSlider";
export const getControlledInputs = (
  formField: ControlledFormElement,
  field: ControllerRenderProps,
  showLabels: boolean,
  organisationType?: string,
) => {
  {
    switch (formField.type) {
      case ControlledFormElementType.SELECT:
        return formField.options ? (
          <ControlledSelect field={field} options={formField.options} showLabels={showLabels} />
        ) : null;
      case ControlledFormElementType.MULTI_SELECT:
        return formField.options ? (
          <ControlledMultiSelect field={field} options={formField.options} />
        ) : null;
      case ControlledFormElementType.BOOLEAN:
        return <ControlledBoolean field={field} showLabels={showLabels} />;
      case ControlledFormElementType.TEXT_AREA:
        return <ControlledTextArea field={field} showLabels={showLabels} />;
      case ControlledFormElementType.TEXT_EDITOR:
        return <ControlledTextEditor field={field} />;
      case ControlledFormElementType.MULTI_EMAIL:
        return <ControlledMultiEmail field={field} />;
      case ControlledFormElementType.FILE:
      case ControlledFormElementType.PDF:
        return <ControlledFile field={field} />;
      case ControlledFormElementType.EXCEL:
        return <ControlledSingleFile field={field} accept=".xlsx,.xls" />;
      case ControlledFormElementType.PASSWORD:
        return <Input type="password" {...field} />;

      case ControlledFormElementType.SEARCH:
        return <ControlledSearch field={field} organisationType={organisationType} />;
      case ControlledFormElementType.SLIDER:
        return formField.sliderOptions ? (
          <ControlledSlider field={field} sliderOptions={formField.sliderOptions} />
        ) : null;
      default:
        return <ControlledText field={field} type={formField.type} showLabels={showLabels} />;
    }
  }
};

export const sanitizeFormData = <T extends Record<string, unknown>>(
  entity: T,
  formFields?: ControlledFormElement[],
): T => {
  const sanitizedData = { ...entity } as T;

  // Map dossiers to dossierFiles for form initialization
  if ("dossiers" in sanitizedData && Array.isArray(sanitizedData.dossiers)) {
    sanitizedData["dossierFiles" as keyof T] = sanitizedData.dossiers as T[Extract<
      keyof T,
      string
    >];
  }

  for (const key in sanitizedData) {
    const value = sanitizedData[key];
    if (value === null || value === undefined) {
      const field = formFields?.find((f) => f.fieldName === key);
      if (
        field?.type === ControlledFormElementType.MULTI_SELECT ||
        field?.type === ControlledFormElementType.MULTI_EMAIL ||
        field?.type === ControlledFormElementType.FILE ||
        field?.type === ControlledFormElementType.PDF
      ) {
        sanitizedData[key] = [] as T[Extract<keyof T, string>];
      } else {
        sanitizedData[key] = "" as T[Extract<keyof T, string>];
      }
    }
  }

  return sanitizedData;
};

/**
 * Prepares form data for backend submission by converting empty strings to null/undefined
 * and removing fields that should not be sent to the backend.
 * This is the inverse of sanitizeFormData.
 */
export const prepareFormDataForSubmission = <T extends Record<string, unknown>>(
  data: T,
  formFields?: ControlledFormElement[],
): T => {
  const preparedData = { ...data } as T;

  const fieldConfigMap = new Map<string, { type: ControlledFormElementType; required: boolean }>();
  formFields?.forEach((field) => {
    fieldConfigMap.set(field.fieldName, { type: field.type, required: field.required ?? false });
  });
  console.log("preparing data:", preparedData);
  for (const key in preparedData) {
    if (Object.prototype.hasOwnProperty.call(preparedData, key)) {
      const value = preparedData[key];
      const fieldConfig = fieldConfigMap.get(key);

      if ((value === "" || value === null || value === undefined) && !fieldConfig?.required) {
        if (
          fieldConfig?.type === ControlledFormElementType.DATE ||
          fieldConfig?.type === ControlledFormElementType.NUMBER ||
          fieldConfig?.type === ControlledFormElementType.URL ||
          fieldConfig?.type === ControlledFormElementType.EMAIL
        ) {
          delete preparedData[key];
        }
      }

      if (Array.isArray(value) && value.length === 0 && !fieldConfig?.required) {
        if (
          fieldConfig?.type === ControlledFormElementType.MULTI_SELECT ||
          fieldConfig?.type === ControlledFormElementType.MULTI_EMAIL
        ) {
          // delete preparedData[key];
        }
      }
    }
  }

  return preparedData;
};

export const createZodFormSchema = (
  formFields: ControlledFormElement[],
): ZodObject<Record<string, ZodType>> => {
  const schema: Record<string, ZodType> = {};

  formFields.forEach((field) => {
    const { fieldName, type, required, multiple, isRegistration } = field;
    let zodType: ZodType;

    switch (type) {
      case ControlledFormElementType.NUMBER:
      case ControlledFormElementType.SLIDER:
        zodType = z.number().optional();
        break;
      case ControlledFormElementType.MULTI_SELECT:
        zodType = z.array(z.string());
        break;
      case ControlledFormElementType.BOOLEAN:
        zodType = z.boolean();
        break;
      case ControlledFormElementType.FILE:
        zodType = z.array(z.instanceof(File));
        break;
      case ControlledFormElementType.EXCEL:
        const ACCEPTED_EXCEL_MIME_TYPES = [
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", // .xlsx
          "application/vnd.ms-excel", // .xls
        ];

        const ACCEPTED_EXCEL_EXTENSIONS = [".xlsx", ".xls"];
        zodType = z.instanceof(File).refine(
          (data) => {
            if (!(data instanceof File)) return false;
            const isValidExtension = ACCEPTED_EXCEL_EXTENSIONS.some((ext) =>
              data.name.toLowerCase().endsWith(ext),
            );
            const isValidMimeType = !data.type || ACCEPTED_EXCEL_MIME_TYPES.includes(data.type);
            return isValidExtension && isValidMimeType;
          },
          {
            message: "Only Excel files (.xlsx, .xls) are allowed.",
          },
        );
        break;
      case ControlledFormElementType.PDF:
        zodType = z
          .array(
            z.union([
              z.instanceof(File),
              z.object({
                id: z.number(),
                file: z.string(),
                uploadedAt: z.date().or(z.string()),
              }),
            ]),
          )
          .refine(
            (items) =>
              items.every((item) => {
                // Only validate File objects, not existing Dossiers
                if (item instanceof File) {
                  return item.type === "application/pdf";
                }
                return true;
              }),
            "Please only submit PDFs",
          );
        break;
      case ControlledFormElementType.DATE:
        zodType = z.string().regex(/^\d{4}-\d{2}-\d{2}$/, "Date must be in the format YYYY-MM-DD");
        break;
      case ControlledFormElementType.PASSWORD:
        if (isRegistration) {
          zodType = z
            .string()
            .min(1, "Password is required")
            .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
            .regex(/[a-z]/, "Password must contain at least one lowercase letter")
            .regex(/\d/, "Password must contain at least one digit")
            .regex(
              /[!@#$%^&*(),.?":{}|<>]/,
              "Password must contain at least one special character",
            );
        } else {
          zodType = z.string().min(1, "Password is required");
        }
        break;
      case ControlledFormElementType.URL:
        zodType = z
          .string()
          .regex(
            /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
            "Please enter a valid URL",
          );
        break;
      case ControlledFormElementType.EMAIL:
        zodType = z.email();
        break;
      case ControlledFormElementType.MULTI_EMAIL:
        zodType = z.array(z.email());
        break;
      case ControlledFormElementType.SEARCH:
        zodType = z.number();
        break;
      case ControlledFormElementType.SMTP:
        zodType = z
          .string()
          .min(1, "SMTP server is required")
          .regex(
            /^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?){2,}$/,
            "Must be a valid hostname (e.g., mail.myserver.com)",
          );
        break;
      case ControlledFormElementType.TEXT:
      case ControlledFormElementType.SELECT:
      case ControlledFormElementType.TEXT_AREA:
      case ControlledFormElementType.TEXT_EDITOR:
      default:
        if (multiple) {
          zodType = z.array(z.string());
        } else {
          zodType = z.string();
        }
        break;
    }

    if (required) {
      if (
        type === ControlledFormElementType.TEXT ||
        type === ControlledFormElementType.SELECT ||
        type === ControlledFormElementType.TEXT_AREA ||
        type === ControlledFormElementType.TEXT_EDITOR
      ) {
        schema[fieldName] = z.string().min(1, "This field is required");
      } else {
        schema[fieldName] = zodType;
      }
    } else {
      schema[fieldName] = zodType.optional().or(z.literal(""));
    }
  });
  return z.object(schema);
};

export const getOptions = <T extends Record<string, string>>(optionsEnum: T): SelectOptions[] => {
  const options = Object.keys(optionsEnum).map((key) => ({
    value: key,
    label: capitalize(optionsEnum[key].replace(/_/g, " ").toLowerCase()),
  }));
  return options;
};

export const getInitialValues = (
  formFields: ControlledFormElement[],
  entity?: Record<string, unknown>,
) => {
  if (entity) return sanitizeFormData(entity, formFields);

  const emptyValues = formFields.reduce(
    (acc, field) => {
      acc[field.fieldName] =
        field.type === ControlledFormElementType.MULTI_SELECT ||
        field.type === ControlledFormElementType.FILE ||
        field.type === ControlledFormElementType.PDF ||
        field.type === ControlledFormElementType.MULTI_EMAIL
          ? []
          : field.type === ControlledFormElementType.EXCEL
            ? null
            : field.type === ControlledFormElementType.BOOLEAN
              ? false
              : // : field.type === ControlledFormElementType.NUMBER
                // ? undefined
                (field.defaultValue ?? "");
      return acc;
    },
    {} as Record<string, unknown>,
  );

  return emptyValues;
};
