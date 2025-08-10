"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useFestival } from "@/context/FestivalContext";
import { getFestivalFormFields } from "../[id]/helpers/getFestivalFormFields";
import { createZodFormSchema, sanitizeFormData } from "@/helpers/formHelper";
import { Festival } from "@/interfaces/Festival";
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table";

interface FestivalDiffFormProps {
  updatedFestival: Festival;
}

const FestivalDiffForm = ({ updatedFestival }: FestivalDiffFormProps) => {
  const { setFestival } = useFestival();
  const router = useRouter();
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(updatedFestival),
  });

  const fields = Object.keys(updatedFestival) as (keyof Festival)[];

  return (
    <form
      onSubmit={form.handleSubmit((values) => {
        setFestival(values as Festival);
        router.push(`/festivals/${updatedFestival.id}`);
      })}
    >
      <Table>
        <TableBody>
          {fields.map((field) => {
            const val = form.watch(field as any) ?? "";
            return (
              <TableRow key={field}>
                <TableCell className="max-w-sm">
                  <input {...form.register(field as any)} defaultValue={val} className="w-full" />
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </form>
  );
};

export default FestivalDiffForm;
