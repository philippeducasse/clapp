"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Check, Mail, Plus, X } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { StatusBadge } from "@/components/common/StatusBadge";
import { inboundEmailApiService } from "@/api/inboundEmailApiService";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { InboundEmail, InboundEmailState, MatchMethod } from "@/interfaces/entities/InboundEmail";
import { ApplicationStatusOptions } from "@/interfaces/forms/StatusOptions";
import { formatDate } from "@/utils/stringUtils";
import ApplicationPicker from "./ApplicationPicker";

const MATCH_METHOD_LABELS: Record<MatchMethod, { label: string; className: string; title: string }> =
  {
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
    [MatchMethod.NONE]: {
      label: "No match",
      className: "bg-slate-100 text-slate-700 border-slate-200",
      title: "No application found",
    },
  };

interface InboundEmailsCardProps {
  applicationId?: number;
  onApproved?: (email: InboundEmail) => void;
}

const InboundEmailsCard = ({ applicationId, onApproved }: InboundEmailsCardProps) => {
  const [emails, setEmails] = useState<InboundEmail[]>([]);
  const [unmatched, setUnmatched] = useState<InboundEmail[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const requests = [
      inboundEmailApiService
        .getAll({ state: InboundEmailState.PENDING_REVIEW, application: applicationId })
        .then((data) => setEmails(data.results)),
    ];
    if (!applicationId) {
      requests.push(
        inboundEmailApiService
          .getAll({ state: InboundEmailState.UNMATCHED })
          .then((data) => setUnmatched(data.results)),
      );
    }
    Promise.all(requests)
      .catch((error) => console.error("Failed to fetch inbound emails:", error))
      .finally(() => setIsLoading(false));
  }, [applicationId]);

  const removeEmail = (id: number) => {
    setEmails((prev) => prev.filter((e) => e.id !== id));
    setUnmatched((prev) => prev.filter((e) => e.id !== id));
  };

  const handleApprove = async (email: InboundEmail, status: ApplicationStatus) => {
    const approved = await inboundEmailApiService.approve(email.id, status);
    removeEmail(email.id);
    onApproved?.(approved);
  };

  const handleLink = async (email: InboundEmail, newApplicationId: number) => {
    const linked = await inboundEmailApiService.link(email.id, newApplicationId);
    removeEmail(email.id);
    // On an application page, the email moved to another application.
    if (!applicationId || linked.application === applicationId) {
      setEmails((prev) => [linked, ...prev]);
    }
  };

  const handleDismiss = async (id: number) => {
    await inboundEmailApiService.dismiss(id);
    removeEmail(id);
  };

  if (applicationId && !isLoading && emails.length === 0) {
    return null;
  }

  const renderList = (list: InboundEmail[], emptyText: string) =>
    isLoading ? (
      <Skeleton className="h-6 w-full" />
    ) : list.length === 0 ? (
      <p className="text-muted-foreground text-sm">{emptyText}</p>
    ) : (
      <div className="space-y-3">
        {list.map((email) => (
          <InboundEmailItem
            key={email.id}
            email={email}
            showApplicationLink={!applicationId}
            onApprove={handleApprove}
            onLink={handleLink}
            onDismiss={handleDismiss}
          />
        ))}
      </div>
    );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-3xl text-primary flex items-center gap-2">
          <Mail /> Replies to review
        </CardTitle>
        <CardDescription className="text-xl">
          Emails about your applications, with a suggested status
        </CardDescription>
      </CardHeader>
      <CardContent>
        {applicationId ? (
          renderList(emails, "No replies waiting for review")
        ) : (
          <Tabs defaultValue="review">
            <TabsList>
              <TabsTrigger value="review">To review ({emails.length})</TabsTrigger>
              <TabsTrigger value="unmatched">Unmatched ({unmatched.length})</TabsTrigger>
            </TabsList>
            <TabsContent value="review" className="mt-3">
              {renderList(emails, "No replies waiting for review")}
            </TabsContent>
            <TabsContent value="unmatched" className="mt-3">
              {renderList(unmatched, "No unmatched emails")}
            </TabsContent>
          </Tabs>
        )}
      </CardContent>
    </Card>
  );
};

interface InboundEmailItemProps {
  email: InboundEmail;
  showApplicationLink: boolean;
  onApprove: (email: InboundEmail, status: ApplicationStatus) => Promise<void>;
  onLink: (email: InboundEmail, applicationId: number) => Promise<void>;
  onDismiss: (id: number) => Promise<void>;
}

const InboundEmailItem = ({
  email,
  showApplicationLink,
  onApprove,
  onLink,
  onDismiss,
}: InboundEmailItemProps) => {
  const [status, setStatus] = useState<ApplicationStatus | "">(email.suggestedStatus);
  const [isSubmitting, setIsSubmitting] = useState(false);
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
            {matchMethod && !isUnmatched && (
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
        {isUnmatched ? (
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
            <Select
              value={status}
              onValueChange={(value) => setStatus(value as ApplicationStatus)}
            >
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
