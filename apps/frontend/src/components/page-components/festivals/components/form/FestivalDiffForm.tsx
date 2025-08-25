"use client";

import React, { Dispatch, SetStateAction, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { isEqual } from "lodash";
import { getFestivalFormFields } from "../../helpers/getFestivalFormFields";
import { createZodFormSchema, sanitizeFormData, getControlledInputs } from "@/helpers/formHelper";
import { Festival } from "@/interfaces/Festival";
import { Form, FormField, FormItem, FormMessage, FormControl, FormDescription } from "@/components/ui/form";
import { TableCell, TableRow } from "@/components/ui/table";

interface FestivalDiffFormProps {
  updatedFestival: Festival;
  changedFields?: (keyof Festival)[];
  setUpdated: Dispatch<SetStateAction<Festival | undefined>>;
  showLabels: boolean;
}

const FestivalDiffForm: React.FC<FestivalDiffFormProps> = ({
  updatedFestival,
  changedFields = [],
  setUpdated,
  showLabels,
}) => {
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(updatedFestival) as z.infer<typeof formSchema>,
  });

  const watchedValues = form.watch();

  useEffect(() => {
    const updated = { ...updatedFestival, ...watchedValues };
    if (!isEqual(updated, updatedFestival)) {
      setUpdated(updated);
    }
  }, [watchedValues, updatedFestival, setUpdated]);

  return (
    <Form {...form}>
      {formFields
        .filter((ff) => !ff.hidden)
        .map((formField) => {
          const isChanged = changedFields.includes(formField.fieldName as keyof Festival);

          return (
            <TableRow key={formField.fieldName} className={isChanged ? "bg-emerald-50" : undefined}>
              <TableCell className="align-top w-full">
                <FormField
                  control={form.control}
                  name={formField.fieldName as string}
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>{getControlledInputs(formField, field, showLabels)}</FormControl>
                      {showLabels && formField.helpText && <FormDescription>{formField.helpText}</FormDescription>}
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </TableCell>
            </TableRow>
          );
        })}
    </Form>
  );
};

export default FestivalDiffForm;
