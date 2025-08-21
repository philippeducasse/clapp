"use client";
import React from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useFestival } from "@/context/FestivalContext";
import { getFestivalFormFields } from "../../helpers/getFestivalFormFields";
import { createZodFormSchema, sanitizeFormData } from "@/helpers/formHelper";
import { Festival } from "@/interfaces/Festival";
import { Table, TableBody, TableCell, TableRow } from "@/components/ui/table";

interface FestivalDiffFormProps {
  updatedFestival: Festival;
  changedFields: (keyof Festival)[];
}

const FestivalDiffForm = ({ updatedFestival, changedFields }: FestivalDiffFormProps) => {
  const { setFestival } = useFestival();
  const router = useRouter();
  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(updatedFestival),
  });

  const fields = Object.keys(updatedFestival) as (keyof Festival)[];

  const onSubmit = (values: Festival) => {
    console.log("VALS: ", values);
    setFestival(values as Festival);
    router.push(`/festivals/${updatedFestival.id}`);
  };
  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Table tableWidth={"w-full"}>
        <TableBody>
          {fields
            .filter((f) => f !== "description" && f !== "id")
            .map((field) => (
              <TableRow key={String(field)}>
                <TableCell className={`w-full ${changedFields.includes(field) ? "bg-green-50" : ""}`}>
                  <input
                    {...form.register(field as string)}
                    defaultValue={updatedFestival[field] as string | number}
                    className="w-4/5"
                  />
                </TableCell>
              </TableRow>
            ))}
          <TableRow>
            <TableCell className={`w-full ${changedFields.includes("description") ? "bg-green-50" : ""}`}>
              <textarea
                {...form.register("description")}
                defaultValue={updatedFestival.description as string}
                style={{ resize: "vertical" }}
                className="w-full"
              />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </form>
  );
};

export default FestivalDiffForm;
