"use client";

import React, { Dispatch, SetStateAction, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { isEqual } from "lodash";
import { getVenueFormFields } from "../../helpers/getVenueFormFields";
import {
  createZodFormSchema,
  sanitizeFormData,
  getControlledInputs,
} from "@/helpers/formHelper";
import { Venue } from "@/interfaces/entities/Venue";
import {
  Form,
  FormField,
  FormItem,
  FormMessage,
  FormControl,
} from "@/components/ui/form";
import { TableCell, TableRow } from "@/components/ui/table";

interface VenueDiffFormProps {
  updatedVenue: Venue;
  changedFields?: (keyof Venue)[];
  setUpdated: Dispatch<SetStateAction<Venue | undefined>>;
}

const VenueDiffForm: React.FC<VenueDiffFormProps> = ({
  updatedVenue,
  changedFields = [],
  setUpdated,
}) => {
  const formFields = getVenueFormFields();
  const formSchema = createZodFormSchema(formFields);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(updatedVenue) as z.infer<typeof formSchema>,
  });

  const watchedValues = form.watch();

  useEffect(() => {
    const updated = { ...updatedVenue, ...watchedValues };
    if (!isEqual(updated, updatedVenue)) {
      setUpdated(updated);
    }
  }, [watchedValues, updatedVenue, setUpdated]);

  return (
    <Form {...form}>
      {formFields
        .filter((ff) => !ff.hidden)
        .map((formField) => {
          const isChanged = changedFields.includes(
            formField.fieldName as keyof Venue
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

export default VenueDiffForm;
