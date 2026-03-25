"use client";

import React, { Dispatch, SetStateAction, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { isEqual } from "lodash";
import {
  createZodFormSchema,
  sanitizeFormData,
  getControlledInputs,
} from "@/helpers/formHelper";
import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import {
  Form,
  FormField,
  FormItem,
  FormMessage,
  FormControl,
} from "@/components/ui/form";
import { TableCell, TableRow } from "@/components/ui/table";

export interface GenericDiffFormProps<T> {
  updated: T;
  changedFields?: (keyof T)[];
  setUpdated: Dispatch<SetStateAction<T | undefined>>;
  formFields: ControlledFormElement[];
}

const GenericDiffForm = <T extends Record<string, unknown>>({
  updated,
  changedFields = [],
  setUpdated,
  formFields,
}: GenericDiffFormProps<T>) => {
  const formSchema = createZodFormSchema(formFields);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(updated) as z.infer<typeof formSchema>,
  });

  // eslint-disable-next-line react-hooks/incompatible-library
  const watchedValues = form.watch();

  useEffect(() => {
    const updatedEntity = { ...updated, ...watchedValues };
    if (!isEqual(updatedEntity, updated)) {
      setUpdated(updatedEntity);
    }
  }, [watchedValues, updated, setUpdated]);

  return (
    <Form {...form}>
      {formFields
        .filter((ff) => !ff.hidden)
        .map((formField) => {
          const isChanged = changedFields.includes(
            formField.fieldName as keyof typeof updated
          );

          return (
            <TableRow
              key={formField.fieldName}
              className={
                isChanged ? "bg-primary/5" : undefined
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

export default GenericDiffForm;
