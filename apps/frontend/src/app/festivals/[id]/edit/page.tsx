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

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

// 1. Define the validation schema with zod
const formSchema = z.object({
  festivalName: z.string().min(1, "Festival name is required"),
  websiteUrl: z.string().url().optional().or(z.literal("")),
  country: z.string().optional(),
  town: z.string().optional(),
  approximateDate: z.string().optional(),
  contactEmail: z.string().email().optional().or(z.literal("")),
  contactPerson: z.string().optional(),
  startDate: z.string().optional(), // ISO date string
  endDate: z.string().optional(),
  festivalType: z.string().optional(),
  description: z.string().optional(),
  applicationType: z.string().optional(),
  applicationStart: z.string().optional(),
  applicationEnd: z.string().optional(),
});

export default function FestivalForm() {
  const festivalData = useFestival();

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log("Submitted data:", values);
    // Add mutation or API update logic here
  }

  const [festival, setFestival] = useState<Festival>(festivalData);

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      festivalName: festival.festivalName ?? "",
      websiteUrl: festival.websiteUrl ?? "",
      country: festival.country ?? "",
      town: festival.town ?? "",
      approximateDate: festival.approximateDate ?? "",
      contactEmail: festival.contactEmail ?? "",
      contactPerson: festival.contactPerson ?? "",
      startDate: festival.startDate?.toISOString().slice(0, 10) ?? "",
      endDate: festival.endDate?.toISOString().slice(0, 10) ?? "",
      festivalType: festival.festivalType ?? "",
      description: festival.description ?? "",
      applicationType: festival.applicationType ?? "",
      applicationStart: festival.applicationStart ?? "",
      applicationEnd: festival.applicationEnd ?? "",
    },
  });

  const handleChange = (field: keyof Festival) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFestival((prev) => ({ ...prev, [field]: e.target.value }));
  };
  console.log({ festival });
  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6 max-w-3xl mx-auto mt-6">
        {[
          ["festivalName", "Festival Name", "The public-facing name of the festival"],
          ["websiteUrl", "Website", "Optional website URL"],
          ["country", "Country", "Country where the festival takes place"],
          ["town", "Town", "Town or city name"],
          ["approximateDate", "Approximate Date", "e.g. 'Early July'"],
          ["contactEmail", "Contact Email", "Email for communication"],
          ["contactPerson", "Contact Person", "Who to reach out to"],
          ["startDate", "Start Date", "Actual or expected start date"],
          ["endDate", "End Date", "Actual or expected end date"],
          ["festivalType", "Festival Type", "e.g. Circus, Theater, Music"],
          ["description", "Description", "A short description of the event"],
          ["applicationType", "Application Type", "e.g. Open call, Curated"],
          ["applicationStart", "Application Start", "When the application opens"],
          ["applicationEnd", "Application End", "When the application closes"],
        ].map(([name, label, desc]) => (
          <FormField
            key={name}
            control={form.control}
            name={name as keyof z.infer<typeof formSchema>}
            render={({ field }) => (
              <FormItem>
                <FormLabel>{label}</FormLabel>
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
