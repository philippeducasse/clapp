"use client";

import React, { Dispatch, SetStateAction, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { isEqual } from "lodash";
import { getResidencyFormFields } from "../../helpers/form/getResidencyFormFields";
import {
  createZodFormSchema,
  sanitizeFormData,
  getControlledInputs,
} from "@/helpers/formHelper";
import { Residency } from "@/interfaces/entities/Residency";
import {
  Form,
  FormField,
  FormItem,
  FormMessage,
  FormControl,
} from "@/components/ui/form";
import { TableCell, TableRow } from "@/components/ui/table";

interface ResidencyDiffFormProps {
  updatedResidency: Residency;
  changedFields?: (keyof Residency)[];
  setUpdated: Dispatch<SetStateAction<Residency | undefined>>;
}

const ResidencyDiffForm: React.FC<ResidencyDiffFormProps> = ({
  updatedResidency,
  changedFields = [],
  setUpdated,
}) => {
  const formFields = getResidencyFormFields();
  const formSchema = createZodFormSchema(formFields);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(updatedResidency) as z.infer<typeof formSchema>,
  });

  const watchedValues = form.watch();

  useEffect(() => {
    const updated = { ...updatedResidency, ...watchedValues };
    if (!isEqual(updated, updatedResidency)) {
      setUpdated(updated);
    }
  }, [watchedValues, updatedResidency, setUpdated]);

  return (
    <Form {...form}>
      {formFields
        .filter((ff) => !ff.hidden)
        .map((formField) => {
          const isChanged = changedFields.includes(
            formField.fieldName as keyof Residency
          );

          return (
            <TableRow
              key={formField.fieldName}
              className={
                isChanged ? "bg-emerald-50 dark:bg-emerald-950" : undefined
              }
            >
              <TableCell className="align-top w-full">
                <FormField
                  control={form.control}
                  name={formField.fieldName as string}
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        {getControlledInputs(formField, field, false)}
                      </FormControl>
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

export default ResidencyDiffForm;
