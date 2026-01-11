"use client";

import { useEffect } from "react";
import { useSelector } from "react-redux";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAppDispatch } from "@/redux/hook";
import { fetchFestivals, selectAllFestivals } from "@/redux/slices/festivalSlice";
import { fetchApplications, selectAllApplications } from "@/redux/slices/applicationSlice";
import { fetchVenues, selectAllVenues } from "@/redux/slices/venueSlice";
import { fetchResidencies, selectAllResidencies } from "@/redux/slices/residencySlice";
import { selectProfile } from "@/redux/slices/authSlice";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import { Progress } from "@/components/ui/progress";

const Page = () => {
  const dispatch = useAppDispatch();
  const festivals = useSelector(selectAllFestivals);
  const applications = useSelector(selectAllApplications);
  const venues = useSelector(selectAllVenues);
  const residencies = useSelector(selectAllResidencies);
  const profile = useSelector(selectProfile);

  useEffect(() => {
    if (festivals.length === 0) {
      dispatch(fetchFestivals());
    }
    if (applications.length === 0) {
      dispatch(fetchApplications());
    }
    if (venues.length === 0) {
      dispatch(fetchVenues());
    }
    if (residencies.length === 0) {
      dispatch(fetchResidencies());
    }
  }, [dispatch, festivals.length, applications.length, venues.length, residencies.length]);

  // Calculate application statistics
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

  // Calculate profile completion
  const calculateProfileCompletion = () => {
    if (!profile) return { percentage: 0, completed: 0, total: 0, missingFields: [] };

    const fields = [
      { name: "First Name", value: profile.firstName },
      { name: "Last Name", value: profile.lastName },
      { name: "Company Name", value: profile.companyName },
      { name: "Personal Website", value: profile.personalWebsite },
      { name: "Location", value: profile.location },
      { name: "Nationality", value: profile.nationality },
      {
        name: "Spoken Languages",
        value: profile.spokenLanguages && profile.spokenLanguages.length > 0,
      },
      { name: "Instagram Profile", value: profile.instagramProfile },
      { name: "Facebook Profile", value: profile.facebookProfile },
      { name: "TikTok Profile", value: profile.tiktokProfile },
      { name: "YouTube Profile", value: profile.youtubeProfile },
      { name: "Performances", value: profile.performances && profile.performances.length > 0 },
      { name: "Email Configuration", value: profile.emailHost && profile.emailHostUser },
    ];

    const completed = fields.filter((field) => field.value).length;
    const total = fields.length;
    const percentage = Math.round((completed / total) * 100);
    const missingFields = fields.filter((field) => !field.value).map((field) => field.name);

    return { percentage, completed, total, missingFields };
  };

  const profileCompletion = calculateProfileCompletion();

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-emerald-600 dark:text-emerald-400">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back! Here&apos;s your performance career overview.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Applications</CardDescription>
            <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">
              {applications.length}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">All submissions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Festivals</CardDescription>
            <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">
              {festivals.length}
            </CardTitle>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Residencies</CardDescription>
            <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">
              {residencies.length}
            </CardTitle>
          </CardHeader>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Venues</CardDescription>
            <CardTitle className="text-3xl text-emerald-600 dark:text-emerald-400">
              {venues.length}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Takes 2/3 */}
        <div className="lg:col-span-2 space-y-6">
          {/* Application Details */}
          <Card>
            <CardHeader>
              <CardTitle className="text-emerald-600 dark:text-emerald-400">
                Application Breakdown
              </CardTitle>
              <CardDescription>Detailed status of all your applications</CardDescription>
            </CardHeader>
            <CardContent>
              {applications.length === 0 ? (
                <div className="text-muted-foreground text-sm">No applications yet</div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="space-y-1">
                    <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
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
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-emerald-600 dark:text-emerald-400">
                Profile Completion
              </CardTitle>
              <CardDescription>
                Complete your profile to improve application success
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {!profile ? (
                <div className="text-muted-foreground text-sm">Loading profile...</div>
              ) : (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
                      {profileCompletion.percentage}%
                    </span>
                    <span className="text-sm text-muted-foreground">
                      {profileCompletion.completed} of {profileCompletion.total} fields completed
                    </span>
                  </div>
                  <Progress
                    value={profileCompletion.percentage}
                    className="h-2"
                    color="emerald-600"
                  />
                  {profileCompletion.missingFields.length > 0 && (
                    <div className="space-y-2">
                      <p className="text-sm font-medium">Missing fields:</p>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        {profileCompletion.missingFields.slice(0, 5).map((field) => (
                          <li key={field} className="flex items-center gap-2">
                            <span className="size-1.5 rounded-full bg-muted-foreground" />
                            {field}
                          </li>
                        ))}
                        {profileCompletion.missingFields.length > 5 && (
                          <li className="text-xs italic">
                            +{profileCompletion.missingFields.length - 5} more fields
                          </li>
                        )}
                      </ul>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-emerald-600 dark:text-emerald-400">
                Upcoming Deadlines
              </CardTitle>
              <CardDescription>Application deadlines and important dates</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-muted-foreground text-sm">Feature coming soon!</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Page;
