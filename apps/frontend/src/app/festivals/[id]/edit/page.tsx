"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useFestival } from "@/context/FestivalContext";

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
  type: z.string().optional(),
  description: z.string().optional(),
  applicationType: z.string().optional(),
  applicationStart: z.string().optional(),
  applicationEnd: z.string().optional(),
});

export default function FestivalForm() {
  const festival = useFestival();

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
      type: festival.type ?? "",
      description: festival.description ?? "",
      applicationType: festival.applicationType ?? "",
      applicationStart: festival.applicationStart ?? "",
      applicationEnd: festival.applicationEnd ?? "",
    },
  });

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log("Submitted data:", values);
    // Add mutation or API update logic here
  }

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
          ["type", "Type", "e.g. Circus, Theater, Music"],
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
                  <Input
                    type={name.includes("Date") ? "date" : name.includes("Type") ? "submit" : "text"}
                    {...field}
                    value={festival[field.name]}
                  />
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
