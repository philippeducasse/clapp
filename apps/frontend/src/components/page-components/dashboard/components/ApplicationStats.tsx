import React from "react";
import { Application, ApplicationStatus } from "@/interfaces/entities/Application";

const ApplicationStats = ({ applications }: { applications: Application[] }) => {
  const applicationStats = {
    accepted: applications.filter((app) => app.status === ApplicationStatus.ACCEPTED).length,
    rejected: applications.filter((app) => app.status === ApplicationStatus.REJECTED).length,
    inDiscussion: applications.filter((app) => app.status === ApplicationStatus.IN_DISCUSSION)
      .length,
    applied: applications.filter((app) => app.status === ApplicationStatus.APPLIED).length,
    draft: applications.filter((app) => app.status === ApplicationStatus.DRAFT).length,
    ignored: applications.filter((app) => app.status === ApplicationStatus.IGNORED).length,
    postponed: applications.filter((app) => app.status === ApplicationStatus.POSTPONED).length,
    cancelled: applications.filter((app) => app.status === ApplicationStatus.CANCELLED).length,
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="space-y-1">
        <p className="text-2xl font-bold text-primary">
          {applicationStats.accepted}
        </p>
        <p className="text-sm text-muted-foreground">Accepted</p>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-red-600 dark:text-red-400">
          {applicationStats.rejected}
        </p>
        <p className="text-sm text-muted-foreground">Rejected</p>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">
          {applicationStats.inDiscussion}
        </p>
        <p className="text-sm text-muted-foreground">In Discussion</p>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
          {applicationStats.applied}
        </p>
        <p className="text-sm text-muted-foreground">Applied</p>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-gray-600 dark:text-gray-400">
          {applicationStats.draft}
        </p>
        <p className="text-sm text-muted-foreground">Draft</p>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">
          {applicationStats.ignored}
        </p>
        <p className="text-sm text-muted-foreground">Ignored</p>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-orange-600 dark:text-orange-400">
          {applicationStats.postponed}
        </p>
        <p className="text-sm text-muted-foreground">Postponed</p>
      </div>
      <div className="space-y-1">
        <p className="text-2xl font-bold text-slate-600 dark:text-slate-400">
          {applicationStats.cancelled}
        </p>
        <p className="text-sm text-muted-foreground">Cancelled</p>
      </div>
    </div>
  );
};

export default ApplicationStats;
