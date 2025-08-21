"use client";
import React, { Dispatch, SetStateAction, useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { getFestivalFormFields } from "../../helpers/getFestivalFormFields";
import { createZodFormSchema, sanitizeFormData } from "@/helpers/formHelper";
import { Festival } from "@/interfaces/Festival";
import { Form } from "@/components/ui/form";
import { Table, TableBody } from "@/components/ui/table";
import { createFormComponents } from "@/helpers/formHelper";
import { isEqual } from "lodash";

interface FestivalDiffFormProps {
  updatedFestival: Festival;
  changedFields: (keyof Festival)[];
  setUpdated: Dispatch<SetStateAction<Festival | undefined>>;
}

const FestivalDiffForm = ({ updatedFestival, setUpdated }: FestivalDiffFormProps) => {
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(updatedFestival),
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
      <div className="w-full">
        <Table>
          <TableBody className="gap-2">{createFormComponents(formFields, form, false)}</TableBody>
        </Table>
      </div>
    </Form>
  );
};

export default FestivalDiffForm;
