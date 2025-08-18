"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useFestival } from "@/context/FestivalContext";
import { getFestivalFormFields } from "../helpers/getFestivalFormFields";
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

  const fields = Object.keys(updatedFestival).filter((k) => k !== "id") as (keyof Festival)[];

  return (
    <form
      onSubmit={form.handleSubmit((values) => {
        setFestival(values as Festival);
        router.push(`/festivals/${updatedFestival.id}`);
      })}
    >
      <Table tableWidth={"w-full"}>
        <TableBody>
          {fields.map((field) => {
            const val = form.watch(field as any) ?? "";
            return (
              <TableRow key={field} className="f-full">
                <TableCell className="w-full">
                  <input {...form.register(field as any)} defaultValue={val as string | number} className="w-full" />
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
