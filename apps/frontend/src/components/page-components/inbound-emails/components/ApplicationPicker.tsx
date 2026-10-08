"use client";

import { useEffect, useState } from "react";
import { Link2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { StatusBadge } from "@/components/common/StatusBadge";
import { applicationApiService } from "@/api/applicationApiService";
import { Application } from "@/interfaces/entities/Application";

interface ApplicationPickerProps {
  label: string;
  disabled?: boolean;
  excludeId?: number | null;
  onSelect: (applicationId: number) => Promise<void>;
}

const ApplicationPicker = ({ label, disabled, excludeId, onSelect }: ApplicationPickerProps) => {
  const [open, setOpen] = useState(false);
  const [applications, setApplications] = useState<Application[] | null>(null);

  useEffect(() => {
    if (!open || applications) return;
    applicationApiService
      .getAll({ limit: 10000 })
      .then((data) => setApplications(data.results))
      .catch((error) => console.error("Failed to fetch applications:", error));
  }, [open, applications]);

  const handleSelect = async (applicationId: number) => {
    setOpen(false);
    await onSelect(applicationId);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button size="sm" variant="outline" disabled={disabled}>
          <Link2 /> {label}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="start">
        <Command>
          <CommandInput placeholder="Search applications..." />
          <CommandList>
            <CommandEmpty>{applications ? "No application found" : "Loading..."}</CommandEmpty>
            {applications
              ?.filter((application) => application.id !== excludeId)
              .map((application) => (
                <CommandItem
                  key={application.id}
                  value={`${application.organisation?.name ?? ""} ${application.season ?? ""} ${application.id}`}
                  onSelect={() => handleSelect(application.id as number)}
                  className="flex justify-between gap-2"
                >
                  <span className="truncate">
                    {application.organisation?.name ?? `Application #${application.id}`}
                    {application.season && (
                      <span className="text-muted-foreground"> · {application.season}</span>
                    )}
                  </span>
                  <StatusBadge status={application.status} />
                </CommandItem>
              ))}
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
};

export default ApplicationPicker;
