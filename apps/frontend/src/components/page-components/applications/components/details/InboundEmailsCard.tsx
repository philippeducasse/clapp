"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Check, Mail, X } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/common/StatusBadge";
import { inboundEmailApiService } from "@/api/inboundEmailApiService";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { InboundEmail, InboundEmailState } from "@/interfaces/entities/InboundEmail";
import { ApplicationStatusOptions } from "@/interfaces/forms/StatusOptions";
import { formatDate } from "@/utils/stringUtils";

interface InboundEmailsCardProps {
  applicationId?: number;
  onApproved?: (email: InboundEmail) => void;
}

const InboundEmailsCard = ({ applicationId, onApproved }: InboundEmailsCardProps) => {
  const [emails, setEmails] = useState<InboundEmail[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    inboundEmailApiService
      .getAll({ state: InboundEmailState.PENDING_REVIEW, application: applicationId })
      .then((data) => setEmails(data.results))
      .catch((error) => console.error("Failed to fetch inbound emails:", error))
      .finally(() => setIsLoading(false));
  }, [applicationId]);

  const removeEmail = (id: number) => setEmails((prev) => prev.filter((e) => e.id !== id));

  const handleApprove = async (email: InboundEmail, status: ApplicationStatus) => {
    const approved = await inboundEmailApiService.approve(email.id, status);
    removeEmail(email.id);
    onApproved?.(approved);
  };

  const handleDismiss = async (id: number) => {
    await inboundEmailApiService.dismiss(id);
    removeEmail(id);
  };

  if (applicationId && !isLoading && emails.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-3xl text-primary flex items-center gap-2">
          <Mail /> Replies to review
        </CardTitle>
        <CardDescription className="text-xl">
          Replies to your applications, with a suggested status
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <Skeleton className="h-6 w-full" />
        ) : emails.length === 0 ? (
          <p className="text-muted-foreground text-sm">No replies waiting for review</p>
        ) : (
          emails.map((email) => (
            <InboundEmailItem
              key={email.id}
              email={email}
              showApplicationLink={!applicationId}
              onApprove={handleApprove}
              onDismiss={handleDismiss}
            />
          ))
        )}
      </CardContent>
    </Card>
  );
};

interface InboundEmailItemProps {
  email: InboundEmail;
  showApplicationLink: boolean;
  onApprove: (email: InboundEmail, status: ApplicationStatus) => Promise<void>;
  onDismiss: (id: number) => Promise<void>;
}

const InboundEmailItem = ({
  email,
  showApplicationLink,
  onApprove,
  onDismiss,
}: InboundEmailItemProps) => {
  const [status, setStatus] = useState<ApplicationStatus | "">(email.suggestedStatus);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const run = async (action: () => Promise<void>) => {
    setIsSubmitting(true);
    try {
      await action();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="p-3 rounded-lg border space-y-2">
      <div className="flex justify-between items-start gap-2">
        <div className="min-w-0">
          {showApplicationLink && (
            <Link
              href={`/applications/${email.application}`}
              className="text-primary hover:underline"
            >
              {email.organisationName ?? `Application #${email.application}`}
            </Link>
          )}
          <p className="font-medium break-words">{email.subject}</p>
          <p className="text-sm text-muted-foreground">
            {email.fromAddress}
            {email.receivedAt && ` · ${formatDate(email.receivedAt)}`}
          </p>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          <StatusBadge status={email.applicationStatus} />
          {email.suggestedStatus && (
            <>
              <span className="text-muted-foreground">→</span>
              <StatusBadge status={email.suggestedStatus} />
            </>
          )}
        </div>
      </div>

      {email.summary && <p className="italic">{email.summary}</p>}

      <details>
        <summary className="cursor-pointer text-sm text-muted-foreground">Show email</summary>
        <pre className="mt-2 whitespace-pre-wrap text-sm font-sans max-h-80 overflow-y-auto">
          {email.body}
        </pre>
      </details>

      <div className="flex flex-wrap items-center gap-2">
        <Select value={status} onValueChange={(value) => setStatus(value as ApplicationStatus)}>
          <SelectTrigger className="w-44">
            <SelectValue placeholder="Choose a status" />
          </SelectTrigger>
          <SelectContent>
            {ApplicationStatusOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          size="sm"
          disabled={!status || isSubmitting}
          onClick={() => run(() => onApprove(email, status as ApplicationStatus))}
        >
          <Check /> Apply status
        </Button>
        <Button
          size="sm"
          variant="outline"
          disabled={isSubmitting}
          onClick={() => run(() => onDismiss(email.id))}
        >
          <X /> Dismiss
        </Button>
      </div>
    </div>
  );
};

export default InboundEmailsCard;
