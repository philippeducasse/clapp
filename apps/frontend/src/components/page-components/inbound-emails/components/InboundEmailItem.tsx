"use client";

import { useState } from "react";
import Link from "next/link";
import { Check, Plus, Undo2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StatusBadge } from "@/components/common/StatusBadge";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { InboundEmail, InboundEmailState, MatchMethod } from "@/interfaces/entities/InboundEmail";
import { ApplicationStatusOptions } from "@/interfaces/forms/StatusOptions";
import { formatDate } from "@/utils/stringUtils";
import ApplicationPicker from "./ApplicationPicker";

const MATCH_METHOD_LABELS: Record<
  MatchMethod,
  { label: string; className: string; title: string }
> = {
  [MatchMethod.HEADER]: {
    label: "Reply",
    className: "bg-green-100 text-green-700 border-green-200",
    title: "Reply to the application email: the match is certain",
  },
  [MatchMethod.SENDER]: {
    label: "Matched by sender",
    className: "bg-amber-100 text-amber-700 border-amber-200",
    title: "The sender is a known contact. Check the application",
  },
  [MatchMethod.DOMAIN]: {
    label: "Matched by domain",
    className: "bg-amber-100 text-amber-700 border-amber-200",
    title: "The sender's domain belongs to the organisation. Check the application",
  },
  [MatchMethod.NAME]: {
    label: "Matched by name",
    className: "bg-amber-100 text-amber-700 border-amber-200",
    title: "The organisation's name appears in the email. Check the application",
  },
  [MatchMethod.FORM]: {
    label: "Form confirmation",
    className: "bg-amber-100 text-amber-700 border-amber-200",
    title: "You applied on the organisation's website form. Create the application from it",
  },
  [MatchMethod.NONE]: {
    label: "No match",
    className: "bg-slate-100 text-slate-700 border-slate-200",
    title: "No application found",
  },
};

interface InboundEmailItemProps {
  email: InboundEmail;
  showApplicationLink: boolean;
  onApprove: (email: InboundEmail, status: ApplicationStatus) => Promise<void>;
  onLink: (email: InboundEmail, applicationId: number) => Promise<void>;
  onDismiss: (id: number) => Promise<void>;
  onRestore?: (id: number) => Promise<void>;
}

const InboundEmailItem = ({
  email,
  showApplicationLink,
  onApprove,
  onLink,
  onDismiss,
  onRestore,
}: InboundEmailItemProps) => {
  const [status, setStatus] = useState<ApplicationStatus | "">(email.suggestedStatus);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const isProcessed =
    email.state === InboundEmailState.APPROVED || email.state === InboundEmailState.DISMISSED;
  const isUnmatched = email.state === InboundEmailState.UNMATCHED || !email.application;
  const matchMethod = MATCH_METHOD_LABELS[email.matchMethod];
  const approvesDraft =
    email.applicationStatus === ApplicationStatus.DRAFT && status === ApplicationStatus.APPLIED;

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
          {showApplicationLink &&
            (email.application ? (
              <Link
                href={`/applications/${email.application}`}
                className="text-primary hover:underline"
              >
                {email.organisationName ?? `Application #${email.application}`}
              </Link>
            ) : (
              email.organisationName && (
                <p className="text-primary">{email.organisationName} (no application)</p>
              )
            ))}
          <p className="font-medium break-words">{email.subject}</p>
          <p className="text-sm text-muted-foreground">
            {email.fromAddress}
            {email.receivedAt && ` · ${formatDate(email.receivedAt)}`}
          </p>
          <div className="flex flex-wrap gap-1 mt-1">
            {matchMethod && (!isUnmatched || email.matchMethod === MatchMethod.FORM) && (
              <Badge variant="outline" className={matchMethod.className} title={matchMethod.title}>
                {matchMethod.label}
              </Badge>
            )}
            {email.isAutoReply && (
              <Badge variant="outline" className="bg-sky-100 text-sky-700 border-sky-200">
                Auto-reply
              </Badge>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1 shrink-0">
          {email.applicationStatus && <StatusBadge status={email.applicationStatus} />}
          {email.suggestedStatus && (
            <>
              <span className="text-muted-foreground">→</span>
              <StatusBadge status={email.suggestedStatus} />
            </>
          )}
        </div>
      </div>

      {email.summary && <p className="italic">{email.summary}</p>}

      {approvesDraft && (
        <p className="text-sm text-amber-700">
          This application is a draft: approving marks it as applied.
        </p>
      )}

      <details>
        <summary className="cursor-pointer text-sm text-muted-foreground">Show email</summary>
        <pre className="mt-2 whitespace-pre-wrap text-sm font-sans max-h-80 overflow-y-auto">
          {email.body}
        </pre>
      </details>

      <div className="flex flex-wrap items-center gap-2">
        {isProcessed ? (
          <>
            <Badge variant="outline">
              {email.state === InboundEmailState.APPROVED ? "Status applied" : "Dismissed"}
            </Badge>
            {onRestore && (
              <Button
                size="sm"
                variant="outline"
                disabled={isSubmitting}
                onClick={() => run(() => onRestore(email.id))}
              >
                <Undo2 /> {email.application ? "Move back to review" : "Move back to unmatched"}
              </Button>
            )}
          </>
        ) : isUnmatched ? (
          <>
            <Button size="sm" asChild disabled={isSubmitting}>
              <Link href={`/applications/create?inboundEmail=${email.id}`}>
                <Plus /> Create application
              </Link>
            </Button>
            <ApplicationPicker
              label="Link to application"
              disabled={isSubmitting}
              onSelect={(applicationId) => run(() => onLink(email, applicationId))}
            />
          </>
        ) : (
          <>
            <Select value={status} onValueChange={(value) => setStatus(value as ApplicationStatus)}>
              <SelectTrigger className="w-48">
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
            <ApplicationPicker
              label="Change application"
              disabled={isSubmitting}
              excludeId={email.application}
              onSelect={(applicationId) => run(() => onLink(email, applicationId))}
            />
          </>
        )}
        {!isProcessed && (
          <Button
            size="sm"
            variant="outline"
            disabled={isSubmitting}
            onClick={() => run(() => onDismiss(email.id))}
          >
            <X /> Dismiss
          </Button>
        )}
      </div>
    </div>
  );
};

export default InboundEmailItem;
