"use client";

import { useEffect, useState } from "react";
import { Mail } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { inboundEmailApiService } from "@/api/inboundEmailApiService";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { InboundEmail, InboundEmailState } from "@/interfaces/entities/InboundEmail";
import InboundEmailItem from "@/components/page-components/inbound-emails/components/InboundEmailItem";

const TABS: { state: InboundEmailState; label: string; emptyText: string }[] = [
  {
    state: InboundEmailState.PENDING_REVIEW,
    label: "To review",
    emptyText: "No emails to review",
  },
  {
    state: InboundEmailState.UNMATCHED,
    label: "Unmatched",
    emptyText: "No unmatched emails",
  },
  {
    state: InboundEmailState.APPROVED,
    label: "Approved",
    emptyText: "No approved emails",
  },
  {
    state: InboundEmailState.DISMISSED,
    label: "Dismissed",
    emptyText: "No dismissed emails",
  },
];

const InboundEmailsPage = () => {
  const [emails, setEmails] = useState<InboundEmail[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    Promise.all(TABS.map((tab) => inboundEmailApiService.getAll({ state: tab.state })))
      .then((responses) => setEmails(responses.flatMap((data) => data.results)))
      .catch((error) => console.error("Failed to fetch inbound emails:", error))
      .finally(() => setIsLoading(false));
  }, []);

  const replaceEmail = (updated: InboundEmail) =>
    setEmails((prev) => prev.map((e) => (e.id === updated.id ? updated : e)));

  const handleApprove = async (email: InboundEmail, status: ApplicationStatus) =>
    replaceEmail(await inboundEmailApiService.approve(email.id, status));

  const handleLink = async (email: InboundEmail, applicationId: number) =>
    replaceEmail(await inboundEmailApiService.link(email.id, applicationId));

  const handleDismiss = async (id: number) =>
    replaceEmail(await inboundEmailApiService.dismiss(id));

  const handleRestore = async (id: number) =>
    replaceEmail(await inboundEmailApiService.restore(id));

  const byNewest = (a: InboundEmail, b: InboundEmail) =>
    (b.receivedAt ?? b.createdAt).localeCompare(a.receivedAt ?? a.createdAt);

  return (
    <div className="container mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl text-primary flex items-center gap-2">
            <Mail /> Inbound emails
          </CardTitle>
          <CardDescription className="text-xl">
            All emails found about your applications. Dismissed or approved emails can be moved back
            to review.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue={InboundEmailState.PENDING_REVIEW}>
            <TabsList>
              {TABS.map((tab) => (
                <TabsTrigger key={tab.state} value={tab.state}>
                  {tab.label} ({emails.filter((e) => e.state === tab.state).length})
                </TabsTrigger>
              ))}
            </TabsList>
            {TABS.map((tab) => {
              const list = emails.filter((e) => e.state === tab.state).sort(byNewest);
              return (
                <TabsContent key={tab.state} value={tab.state} className="mt-3">
                  {isLoading ? (
                    <Skeleton className="h-6 w-full" />
                  ) : list.length === 0 ? (
                    <p className="text-muted-foreground text-sm">{tab.emptyText}</p>
                  ) : (
                    <div className="space-y-3">
                      {list.map((email) => (
                        <InboundEmailItem
                          key={`${email.id}-${email.state}`}
                          email={email}
                          showApplicationLink
                          onApprove={handleApprove}
                          onLink={handleLink}
                          onDismiss={handleDismiss}
                          onRestore={handleRestore}
                        />
                      ))}
                    </div>
                  )}
                </TabsContent>
              );
            })}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default InboundEmailsPage;
