"use client";

import { useEffect, useState } from "react";
import { Mail } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { inboundEmailApiService } from "@/api/inboundEmailApiService";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { InboundEmail, InboundEmailState } from "@/interfaces/entities/InboundEmail";
import InboundEmailItem from "./InboundEmailItem";

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
        .getAll({
          state: InboundEmailState.PENDING_REVIEW,
          application: applicationId,
        })
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

export default InboundEmailsCard;
