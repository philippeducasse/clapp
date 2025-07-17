"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useFestival } from "@/context/FestivalContext";
import { useState } from "react";
import { Festival } from "@/interfaces/Festival";
import { getFestivalFormFields } from "../helpers/getFestivalFormFields";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { createZodFormSchema, sanitizeFormData } from "@/helpers/formHelper";

export default function FestivalForm() {
  const festivalData = useFestival();

  const formFields = getFestivalFormFields();
  const formSchema = createZodFormSchema(formFields);

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log("Submitted data:", values);
    // Add mutation or API update logic here
  }

  const [festival, setFestival] = useState<Festival>(festivalData);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: sanitizeFormData(festival),
  });

  const handleChange = (field: keyof Festival) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFestival((prev) => ({ ...prev, [field]: e.target.value }));
  };
  console.log({ festival });
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 max-w-3xl mx-auto mt-6">
        {formFields.map((formField) => (
          <FormField
            key={formField.fieldName}
            control={form.control}
            name={formField.fieldName as keyof z.infer<typeof formSchema>}
            render={({ field }) => (
              <FormItem>
                <FormLabel>{formField.label}</FormLabel>
                <FormControl>
                  {name === "festivalType" ? (
                    <Select
                      value={field.value}
                      onValueChange={(val) => {
                        field.onChange(val);
                        setFestival((prev) => ({ ...prev, festivalType: val }));
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="STREET">Street</SelectItem>
                        <SelectItem value="CIRCUS">Circus</SelectItem>
                        <SelectItem value="OTHER">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  ) : (
                    <Input
                      type={name.includes("startDate") || name.includes("endDate") ? "date" : "text"}
                      {...field}
                      value={field.value}
                      onChange={(e) => {
                        field.onChange(e);
                        handleChange(field as unknown as keyof Festival)(e);
                      }}
                    />
                  )}
                </FormControl>
                <FormDescription>{desc}</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        ))}

        <Button type="submit">Save Festival</Button>
      </form>
    </Form>
  );
}
